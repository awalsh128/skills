---
name: vsce-demo
description:
  Use when the user wants a demo, GIF, screencast or screenshots of a VS Code extension for its README or
  Marketplace listing, or says "vsce-demo". Builds scripted, re-runnable recordings that cover every feature
  the extension contributes (commands, diagnostics, code actions, providers such as hover, webview panels,
  views, settings). Not for the README wording (use create-readme), publishing (use vsce-project), the
  extension's own code (use typescript) or demos of anything that is not a VS Code extension.
---

# vsce-demo

Make the demo code, not a manual screen capture. Each feature gets a scripted scene that drives a real VS Code
window, and a recorder films it. A hand-made capture goes stale the first time the UI changes and nobody can
reproduce it; a scene is re-run in one command and fails loudly when a feature stops working.

Use create-readme to place the result in the README, vsce-project for what may ship in the `.vsix`, and
typescript for the demo code.

## 1. Inventory every feature

"All features" must be checkable, so the list comes from a script, not from memory. In the extension's folder
(the one with the manifest, so the package folder in a monorepo), run
`python3 <skill dir>/scripts/inventory.py`. It reads two sources that have to agree:

- **Manifest:** every key under `contributes` in `package.json` (commands, menus, keybindings, settings,
  views, languages, grammars, snippets, walkthroughs, custom editors, notebooks, debuggers, tasks, chat
  participants, language model tools and the rest), plus `activationEvents`.
- **Source:** every provider registration, diagnostic collection, webview, tree view, status bar item, test
  controller, decoration type, message or input box, and `onDid...` listener that changes what the user sees.

It prints a skeleton for `demo/COVERAGE.md` with one row per feature id (`command:...`, `setting:...`,
`source:registerHoverProvider`) and a **Findings** list where the manifest and the source disagree (a command
contributed but never registered, or the reverse). Report the findings to the user.

Fill the table: a scene name per row (several ids can share a row; a scene may have a row with no id when it
shows a variant of a feature, such as a setting off), plus the way it is driven (API or xdotool) and what it
resets. Features with no scene go in a "Not demoed" list as a bullet with the id in backticks, a colon and the
reason (needs credentials, needs an outside service, no visible effect). Do not say the demo covers every
feature until `python3 <skill dir>/scripts/check-coverage.py` passes: it fails on any id that is neither
demoed nor excused, a TODO or unknown scene, a scene file missing from `scenes/index.ts` or the table, and
stale ids.

Read `references/feature-recipes.md` for how to seed, drive and assert each kind of feature.

## 2. Layout

Copy `templates/` to `demo/` in the extension's folder. It is the working driver, reset, recorder and fixed
look, already run end to end; read `references/driver.md` for how the pieces fit before changing one.

```text
demo/
  COVERAGE.md        feature id -> scene, or why not
  profile/settings.json   the fixed look every recording uses
  workspace/         seeded files you write; the features fire naturally on them
  scenes/<feature>.ts     one scene per feature, listed in scenes/index.ts
  build.mjs launch.ts index.ts helpers.ts reset.ts record.sh frames.sh probe.sh   (from templates/)
```

Delete `scenes/example-diagnostics.ts` once you have written a real scene. Command IDs and CLI flags are VS
Code internals; when one fails, confirm it against the installed VS Code, and read `references/lessons.md`
when a recording looks wrong.

## 3. Scene rules

- **Drive what a user would.** Use the palette, the lightbulb, hover, typing, the context menu. Call the
  provider APIs (`vscode.execute*Provider`) only to assert, never to stand in for the user's action.
- **Assert before the recording means anything.** A scene throws when the feature did not appear (diagnostics
  empty, hover empty, panel not open, text unchanged after the fix). A silent scene records a blank screen and
  looks fine until someone watches it.
- **Wait on conditions, pause for people.** Async results (language server, worker, webview) use `waitFor`.
  Fixed sleeps are only for pacing: about a second after something appears, two on the final result.
- **Type real keystrokes** with a 40 to 80 ms delay, not a pasted block.
- **One feature per GIF**, 5 to 15 seconds, with a lead-in and a hold on the result.
- **Legible when embedded, and not clipped.** A GIF is shown inside a README column, not full screen, so
  design for the width it is shown at (about 800 px). Record a small window (960x540) and pick the lowest zoom
  that stays readable at that width: start at `window.zoomLevel` 1 with an editor font of 15, and raise it
  only when text is too small. Too much zoom clips what matters (a hover cut off, a webview panel showing only
  its header); too little is unreadable. Check the final GIF frame at its real width for both, and prefer a
  shorter example over a smaller font when a hover or panel still does not fit.
- **Fixed look.** Same theme, font size, window size and layout for every scene, set in the profile, with the
  "Extension Development Host" title and any welcome or tip noise removed. No personal paths, usernames,
  tokens or real data on screen.

## 4. Reset

A demo is only reproducible when every run starts from the same state and leaves nothing behind.

- **Per run (the default):** one VS Code process per scene. `launch.ts` deletes and rebuilds the user-data and
  extensions directories from `demo/profile/` and copies `demo/workspace/` to a temp folder, so edits a scene
  makes (an applied quick fix, a typed pattern) never touch the committed fixture. Extension `globalState`,
  `workspaceState`, secrets and "seen it" flags live in the profile, so a fresh profile is also the "first
  run" state. To demo a "returning user" state, seed it in the profile on purpose.
- **Inside a scene:** anything a scene changes it puts back with `resetState()` in `finally`: settings it set
  (every key under the extension's `configuration`, including `[language]` overrides, back to `undefined`),
  open editors, dirty or modified documents (revert, never save over the fixture), the cursor and selection,
  panels, side bar and layout, notifications, and any panel or view the extension keeps as a singleton. A
  scene that shows a setting off and on ends with it on.
- **Scenes never depend on each other.** Any scene must pass run alone and in any order.
- **Prove it.** Record a scene twice and compare the frame at the ready point; a difference means leaked
  state. Failure also resets: a thrown scene still runs `resetState()` and discards the partial recording.

## 5. Record

`record.sh <scene>` starts a virtual display (Xvfb), launches the scene, starts `ffmpeg` when the driver
signals it is ready, and stops it when the scene ends, then converts to a GIF with a generated palette. Linux
with Xvfb is the default because it does not depend on the user's desktop and runs in CI. On macOS or Windows
only the capture step differs (`avfoundation`, `gdigrab`), and the window must stay uncovered.

On a Wayland desktop Electron opens on the real screen instead of Xvfb and the take is black, so the recorder
forces X11. Needs `Xvfb`, `ffmpeg` and `node`, plus `xdotool` for what the API cannot drive (see recipes). If
one is missing, report it with the install command and stop; do not run an installer with `sudo` yourself.

## 6. Verify

Recording without looking is not done. `record.sh` runs `frames.sh`, which saves the start, middle and end
frames and a contact sheet of the whole GIF to `media/demo/.frames/` at the width the GIF is shown at. Open
them with Read, the sheet first, and check: the feature is visible, the window fills the frame, no dev-host
banner, no personal data, text is legible at the final width. Check the file size too: aim for a few MB at
most, and cut frame rate or width before cutting content.

## 7. Hand off

- Keep `demo/`, its output directory and its dev dependencies out of the `.vsix` through `.vscodeignore`;
  vsce-project's `vsce ls` check fails on stray paths. Let `vsce` rewrite relative README image paths from
  `repository`, as vsce-project describes.
- The Marketplace README renders images; confirm before relying on a video file there. Make a GIF for the
  listing, and keep any video as an extra for GitHub.
- Hand the files to create-readme for placement next to the emoji bullets. Do not write README prose here.
- Read `references/readme-placement.md` only when deciding which GIFs go in the README and which in a gallery
  page; it has the split, the threshold and the registry caveats.
- Binary files make the repo grow on every regeneration. Re-record only the scenes whose feature changed, and
  ASK FIRST before committing or pushing them.

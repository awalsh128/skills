# Driver, reset and recorder

How the pieces in `templates/` fit. Copy the whole folder to `demo/` in the extension's project (the
extension's own folder in a monorepo), then write `demo/scenes/*.ts`. The code is in the files, not here, so
there is one copy and it has been run.

```text
templates/
  build.mjs            bundles demo/index.ts and demo/launch.ts to demo/out/ with esbuild
  launch.ts            fresh profile and temp copy of the workspace per run, then @vscode/test-electron
  index.ts             the in-host runner: activate, reset, signal ready, run the scene, signal done, reset
  helpers.ts           waitFor, openFile, typeText, runFromPalette, findWebviewTab, xdo, positionOf ...
  reset.ts             resetState(): clears every contributed setting and [language] override, reverts and
                       closes editors, closes panels and the side bar, clears notifications
  record.sh            Xvfb, launch, film from "ready" to "done", palette GIF, then frames.sh
  frames.sh            start, mid and end stills plus a contact sheet at the GIF's real width
  probe.sh             holds a state and screenshots it, to read pixel coordinates for xdotool
  profile/settings.json  the fixed look: theme, zoom 1, font 15, no title bar noise
  scenes/index.ts      the list of scenes; scenes/example-diagnostics.ts is a worked example
```

Add `@vscode/test-electron` and `esbuild` as dev dependencies with the project's package manager, build with
`node demo/build.mjs`, and record one scene with `demo/record.sh <scene>`.

## How a run goes

1. `launch.ts` builds a throwaway user-data directory (with `profile/settings.json`), an empty extensions
   directory and a copy of `demo/workspace/`, so nothing a scene does survives the run or touches the fixture.
   Only the extension under development loads.
2. `index.ts` runs inside the extension host. It activates the extension, calls `resetState`, waits for the
   window to settle and writes `DEMO_READY_FILE`; `record.sh` starts filming then.
3. The scene runs. A thrown error ends the run nonzero and `record.sh` discards the take.
4. The runner writes `DEMO_DONE_FILE`, holds for a grace period so the recorder stops first, then resets again
   in `finally`.

## Scene API

A scene is `{ name, languages?, run() }`. `languages` lists the `[language]` overrides it may set so
`resetState` clears them. Put assertions inside `run`; use `waitFor` for anything asynchronous and plain
`sleep` only to pace the viewer.

## What the API cannot reach

Native menus, input boxes and webview contents are driven with `xdo`, `xdoType` and `parkPointer` from
`helpers.ts`. Click targets are pixel coordinates in the fixed 960x540 window. Find them by looking: write a
temporary scene that opens the state and holds it (the context menu with `editor.action.showContextMenu`; a
panel scrolled with four `xdo("click", "5")`), run `demo/probe.sh <scene> shot.png`, Read the PNG, put the
coordinates in constants at the top of the scene and delete the probe scene.

## Notes

- Under Xvfb with no window manager VS Code may not fill the screen. Check the first frame; if it doesn't, run
  `openbox` on the same display, or send `workbench.action.toggleFullScreen` from the driver.
- `xdotool` needs the VS Code window to have focus. With no window manager the window under the pointer gets
  keys, and the window fills the display, so any pointer position inside it works.
- `DEMO_SIZE` changes the capture size (default `960x540`); keep it at the width the GIF is shown at.
- Stills for the Marketplace gallery come from the same take, or from `frames.sh`.
- Command IDs and CLI flags are VS Code internals. When one fails, find the current ID in the Keyboard
  Shortcuts editor and check the flag with `code --help`.
- `demo/`, `media/demo/.frames/` and the dev dependencies stay out of the `.vsix` (`.vscodeignore`).

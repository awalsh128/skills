# Lessons

Failures from building real demos. Each one passed its assertions or ran without error and still produced a
wrong GIF, which is why the skill checks frames. Read this when a recording looks wrong.

- **Black frames, window nowhere:** on a Wayland desktop Electron opens on the real screen and Xvfb stays
  black. `record.sh` unsets `WAYLAND_DISPLAY` and `launch.ts` passes `--ozone-platform=x11`.
- **Black last frames:** filming that stops when the window closes also films the reset and the exit. The
  driver writes a done file and holds for a grace period before resetting; `record.sh` stops on the file.
- **Assertion passes, GIF is wrong:** after a setting turns a hover off, the open hover widget stays on screen
  while the provider already returns nothing. The scene hides it (`editor.action.hideHover`) and the frame
  check confirms it.
- **The last state is gone:** hiding or resetting after the final step empties the closing hold. Leave the
  last thing on screen.
- **Hover or panel clipped:** zoom 2 in a 960x540 window cut a hover and a webview off. Start at zoom 1, font
  15, and shorten the example before shrinking the font.
- **Dev-host chrome:** "Extension Development Host" in the title, a Sign In button, an "extensions disabled"
  toast (from `--disable-extensions`; use an empty `--extensions-dir` instead), and the pointer parked in the
  hover. The profile and `launch.ts` remove the first three; `parkPointer` handles the last.
- **Toasts from built-in extensions:** opening a PHP file raised "Cannot validate since a PHP installation
  could not be found". Silence such toasts in the profile and look for them in the frames.
- **Wrong cursor position:** a scene that hovers `line 3, column 30` breaks when the fixture changes or was
  counted wrong (zero-based lines, a regex that ends earlier). Use `positionOf(document, marker)`.
- **Leftover X server:** a killed run can leave Xvfb on `:99`, and the next launch fails with "Missing X
  server". Check `pgrep Xvfb` before a retry.
- **Passing is not proof:** the run exits 0 when a webview painted late or a pointer sat in the shot. Open the
  frames and the contact sheet from `frames.sh` every time.

# Demos in the README

A demo is any recording or still that shows the product working: an animated GIF, a screenshot, a terminal
recording, a short video. It belongs in the README when a reader has to see the product to understand it, and
nowhere else. The rule behind everything here: **the README has to read and work with every demo removed.**
Demos show; the text explains. A reader on a slow connection, a screen reader, or a registry page that strips
media still gets the whole story.

## Which repos get one

| Product                                                           | Demo shows                                                     | Form                                                     |
| ----------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| Editor extension (VS Code and similar), desktop or web app, site  | The UI doing its main job                                      | GIF or screenshot of the real window                     |
| CLI or TUI                                                        | A real command and its output                                  | Terminal recording as GIF, or a screenshot of the output |
| Library with visual output (charts, rendering, formatting)        | The input and the picture it produces                          | Screenshot or before-and-after image                     |
| GitHub Action, bot, workflow                                      | Its visible effect: a PR comment, a job summary, an annotation | Screenshot                                               |
| Library, skills collection, dotfiles, config, anything non-visual | Nothing                                                        | No demo; never pad                                       |

Use the producing skill when one exists in the session (vsce-demo for a VS Code extension). Otherwise this
file only decides where a demo goes; how it is made is the user's call. If the product is visual and has no
demo, say so in the summary and suggest making one, and write the README without it. Never put a placeholder
or a broken image in the README.

## One hero, a few in place, the rest linked

- **One hero demo** directly under the emoji bullets, before the sponsor badge. It shows the single feature
  the first bullet promises, in 5 to 10 seconds, or one screenshot. It is the only demo above Quick Start;
  Quick Start still comes first among the text sections, and its commands stay copyable text, never only in a
  recording.
- **In-place demos** sit in the section that explains their feature, after the sentence that introduces it and
  before the detail. At most one per section, and at most three or four in the whole README. A feature that is
  only an option or a table gets no demo.
- **Everything else** moves to a gallery, `docs/demos.md`, with one heading and one demo per feature, linked
  once from the README in a `> [!TIP]` callout ("More demos are in the [demo gallery](url)."), right after the
  hero. Do not stack a README full of recordings: each one competes with the text for attention and the page
  stops being scannable. Many demos is a gallery, not a README. Start the gallery at the next feature, not
  with the hero again.

## How each one is written

- **Caption first.** One plain sentence before the image says what to watch for ("Run it on a folder to see
  every duplicate listed."). The reader should know the point before the loop starts.
- **Alt text describes what happens**, not "demo" or "GIF of":
  `Running the command prints the three largest duplicate files`. It is what a screen reader, a blocked image
  and a search engine see.
- **Sized for the column:** `<img src="..." alt="..." width="800">`, the HTML form, which GitHub and the
  registries render. Capture at that width so scaling doesn't blur text. The hero may sit in
  `<p align="center">` to match the header; in-place demos stay left-aligned with the text.
- **Legible:** a reader sees it inside a README column, not full screen, so text in the capture must be
  readable at that width. Zoom the UI or the terminal up rather than shrinking the font.
- **One idea per loop**, with a hold on the result, so a reader who looks away catches the end.
- **Weight:** a few MB each at most, and keep the total the README pulls in small, since a registry page loads
  it all at once. If the demos are heavy, link more of them instead of embedding.
- **Form:** an animated GIF works everywhere a README renders. Video renders on GitHub but many registry pages
  show images only, so confirm where the README is displayed before relying on a video; keep it as an extra
  for the gallery.

## Packaged READMEs

npm, PyPI, crates.io, the Marketplace and Open VSX show the README as it was at the last release, and a
`docs:` commit does not release. So:

- Image URLs must be absolute `https` (or a relative path the packaging tool rewrites from the repository URL;
  check that it does, since npm does not). A relative path that works on GitHub shows as a broken image on the
  registry.
- Link the gallery with an absolute GitHub URL, so it stays current when the packaged copy cannot.
- Keep the demo files in the repo, not in the published package or bundle: add them to the ignore list for the
  packaging tool (`.npmignore` or `files`, `.vscodeignore`, `MANIFEST.in`), and tell the user so.

## Revise and Audit

Revise keeps demos that already exist and moves them into the slots above; it flags extras instead of deleting
them and proposes the gallery for the overflow. Audit reports, per demo: placement (hero under the bullets,
others in their section), caption present, alt text descriptive, width set, count within the limits, URL works
on the registry, Quick Start still the first text section, and the README still readable with the demos
removed.

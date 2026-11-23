# Placing demos in an extension README

Read this when deciding which GIFs go in the README and which go in a gallery page. create-readme's
`references/demos.md` holds the general rule; this file adds what is specific to a VS Code extension.

## The split

Both, divided by how much each demo earns its place:

- **One hero** directly under the emoji bullets, showing the feature the first bullet promises, 5 to 10
  seconds. It is what a reader decides on, so it is never moved to a gallery.
- **In-place demos** (up to three or four in all) in the section that explains the feature, after the sentence
  that introduces it and before the detail: a save behavior section, a panel section, a settings effect.
- **Everything else** in `docs/demos.md`, one heading and one demo per feature, linked once from the README
  with an absolute GitHub URL. Start the gallery at the next feature, not with the hero again, and keep any
  older video there as an extra.

## The threshold

Count the scenes that survive the inventory, not the features:

- **Four or fewer:** put them all in the README and skip the gallery.
- **Five or more:** hero, up to three in place, the rest in the gallery. Measured examples: five GIFs at 1.5
  MB total sit near the line (two in the README, three in the gallery); thirteen GIFs at 7.3 MB need the
  gallery, because the Marketplace and Open VSX load every image at once and thirteen loops make the page
  unscannable.
- **Weight:** a few MB for everything the README pulls in. Past that, link more and embed fewer.

## Extension specifics

- **The listing is frozen.** The Marketplace and Open VSX show the README as of the last release, and a
  `docs:` commit does not release, so new GIFs reach the listing only with the next `fix` or `feat` release.
  Say so when handing off. A dry run of the publish workflow reports "no release" when only docs changed.
- **Image URLs.** Relative paths work on GitHub, and `vsce` rewrites them from `repository` when packaging,
  but only to the default branch, so they stay broken until the GIFs are on it. Absolute raw URLs work
  earlier. Use whichever the repo already uses, and do not mix them.
- **Keep the files out of the package.** `demo/` and the GIF directory go in `.vscodeignore`; check with
  `vsce ls`. The README's images load from the repository, not from the `.vsix`.
- **The README must read without them.** Registries and screen readers may strip images. Each demo has a
  caption sentence before it and alt text that says what happens, never "demo" or "GIF".
- **Size to the column.** `<img ... width="800">`, hero optionally in `<p align="center">`, in-place demos
  left-aligned. Text in the capture must be readable at that width.
- **Moving a demo is not re-recording it.** Re-record only the scenes whose feature changed, and ask before
  committing binaries, since every regeneration grows the repository.

## Checking a placement

Hero under the bullets and the only demo above Quick Start; each in-place demo captioned and in its own
section; the rest in the gallery; the gallery linked once with an absolute URL; the README still complete with
every image removed.

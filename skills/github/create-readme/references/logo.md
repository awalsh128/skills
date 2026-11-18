# Creating a placeholder logo

Read this only after the user says yes to the logo offer (see the Logo convention in `SKILL.md`). The result
is a placeholder: say so in the summary, and never add it without a yes.

## Better tool available?

If this session already lists a design, logo or image-generation skill or tool, offer the user the choice: use
it for a real logo, or write the placeholder below. Do not name, require or ask the user to install anything.
With nothing like that available, go straight to the placeholder. Either way, wire the result in as described
under Steps.

## Steps

1. Write `assets/logo.svg` (create `assets/` if needed). For a VS Code extension the Marketplace icon in
   `package.json` must be a PNG, so keep the SVG for the README and tell the user the icon still needs a PNG.
2. Wire it into the README per the repo type's header: inline `<img ... height="60" align="center">` in the
   title, or the centered block for VS Code extensions. Use `alt="<project name> logo"`.
3. Tell the user it is a placeholder and where to replace it.

## SVG rules

- Self-contained: no external fonts, images or scripts. Use basic shapes and `<text>` with a generic stack
  (`system-ui, sans-serif`).
- `viewBox="0 0 128 128"`, no fixed `width`/`height` on the root, so it scales.
- Readable on both light and dark GitHub themes: a filled rounded square with a contrasting glyph, not a dark
  glyph on a transparent background.
- A concept, not initials, whenever one is available: see **Choosing the concept**. Initials are the last
  resort.
- Simple geometry only: 2-3 shapes, 2-3 colours, no gradients or fine detail, legible at 32px.
- Include a `<title>` with the project name for accessibility.

## Choosing the concept

A better placeholder hints at what the product _does_ through a metaphor, rather than spelling its name.
Exemplar: https://github.com/awalsh128/semantic-release-sentinel-app/blob/staging/assets/icon.svg. It never
draws a "release" or a version number. A **shield** says sentinel (guard, protect) and an **up arrow** inside
it says release (move forward), on a dark rounded square with one accent colour.

1. State the product's job in a few words (for example "guards releases", "keeps lists sorted", "caches
   packages").
2. Pick 1-2 plain objects that metaphorically carry it (shield, arrow, box, funnel, lock, check, brackets).
   Combine at most two: a container plus an action works well.
3. Draw them as bold filled shapes on a dark rounded square, with a light stroke or a light second shape for
   contrast.
4. Fall back to the initials template only when no clear metaphor exists, and say so.

Shape of the exemplar (adapt the paths, don't copy them):

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="NAME icon">
  <rect width="512" height="512" rx="96" fill="#1f2937"/>
  <path d="CONTAINER SHAPE" fill="#10b981" stroke="#ecfdf5" stroke-width="16" stroke-linejoin="round"/>
  <path d="ACTION SHAPE" fill="#ecfdf5"/>
</svg>
```

Use `aria-label` or `<title>` for the accessible name. Say in the summary which metaphor you chose and why, so
the user can redirect it.

## Initials template (fallback)

Use only when no metaphor fits. Replace `AB` with the project's initials (max 2 characters) and `PROJECT NAME`
(the plain-English project name). Use `#1f6feb` unless the repo already has a brand colour in its docs or
config.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img">
  <title>PROJECT NAME logo</title>
  <rect width="128" height="128" rx="24" fill="#1f6feb"/>
  <text x="64" y="64" text-anchor="middle" dominant-baseline="central"
        font-family="system-ui, sans-serif" font-size="56" font-weight="700"
        fill="#ffffff">AB</text>
</svg>
```

## Check

- Render the SVG if a tool is available (e.g. `rsvg-convert`, a browser) and confirm the glyph is centred and
  not clipped; otherwise say it was not rendered.
- The `<img>` path in the README matches the file you wrote.

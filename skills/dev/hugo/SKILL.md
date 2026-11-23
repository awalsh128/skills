---
name: hugo
description:
  Use when the task creates, changes or reviews a Hugo site's content, config, layouts, assets or theme
  overrides, or the user says "hugo". Applies page bundles, assets pipelines, small theme overrides and a
  clean build. Not for one theme's own options (read that theme's docs), CI workflows (use github-cicd) or the
  wording of posts (use my-writing-style).
---

# hugo

Based on [spech66/hugo-best-practices](https://github.com/spech66/hugo-best-practices). Where the repo's own
`AGENTS.md` disagrees, the repo wins.

## Rules

- **Content:** one page bundle per post or page (`content/posts/slug/index.md` with its images beside it).
  Keep folder names lowercase with no spaces. They become the URL unless `slug` or `url` is set, so never
  rename a published one.
- **Assets:** put CSS, JS and images that Hugo processes in `assets/`, not `static/`. Build them with
  `resources.Get | minify | fingerprint`, and load page-specific scripts only on the pages that need them.
- **Images:** keep the original full size and let Hugo resize it (`.Process`, WebP). Set `width` and `height`
  on every `img`, `loading="lazy"` below the fold and `fetchpriority="high"` on the first large image. A
  decorative image that fills a fixed-size box (`absolute inset-0 object-cover`) can't shift the layout and
  may vary in aspect ratio, so it can skip `width` and `height`, but it still needs `alt=""`.
- **Theme:** change as little as possible. Prefer a theme parameter, then a hook partial, then an override in
  the site's `layouts/` or `assets/`. Never edit files inside `themes/` or a theme module. Delete an override
  that is identical to the theme's.
- **Layouts:** use the current layout names (`layouts/_partials/`, `layouts/_shortcodes/`, `layouts/home.html`
  rather than `_default/` and `index.html`) unless the site's minimum Hugo version is older than 0.146.
- **Markup:** build JSON-LD with a `dict | jsonify`, never by templating a string. Handle external links in a
  render hook (`layouts/_markup/render-link.html`), not by editing each link.
- **Config:** set `enableRobotsTXT = true`, a `[sitemap]`, and `[permalinks]` for each content type.
  Git-ignore `public/`, `resources/_gen/` and `.hugo_build.lock`.

## Verify

Build with `hugo --gc --minify --logLevel info`, then grep the output for `deprecat` and fix every warning,
for example `languageCode` to `locale`, `paginate` to `[pagination] pagerSize` and `.Site.Data` to
`hugo.Data`. A site is done when it builds with no warnings.

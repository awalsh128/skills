# Sponsor badge

Placed after the bullets, on by default, for solo-owner projects. A centered pink for-the-badge badge linking
to the owner's Sponsors page, then a short centered pitch that says the project is free, why a sponsor helps,
and that a small one-time donation is fine:

```html
<!-- prettier-ignore -->
<p align="center">
  <a href="https://github.com/sponsors/<owner>"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Sponsor <owner>"></a>
</p>

<p align="center">
  Free and open source, and kept up by one person.<br />
  If it saves you time, <a href="https://github.com/sponsors/<owner>">sponsor it monthly</a> or
  <a href="https://github.com/sponsors/<owner>?frequency=one-time">leave a small one-time tip</a>. Every bit
  helps.
</p>
```

Keep the pitch to two short lines: no heading, no emoji beyond the badge's heart, no guilt. The
`?frequency=one-time` link opens GitHub's one-time tab; if the owner's page has no one-time tier, drop that
link and keep the monthly one. Use the `<!-- prettier-ignore -->` comment only when the repo uses Prettier.
Exemplar: https://github.com/awalsh128/skills.

`<owner>` is the git remote owner. Check the page exists with the GraphQL field `hasSponsorsListing`:
`gh api graphql -f query='{user(login:"<owner>"){hasSponsorsListing}}'` (use `organization(login:...)` for an
org). `false` means no Sponsors page. Do not use a REST `.../sponsorship` path: it does not exist and always
returns 404, which looks like "not found" for owners who do have a page. If GraphQL is unavailable, fetch
`https://github.com/sponsors/<owner>`: a 200 means the page exists, and a 404 or a redirect to the profile
page means it does not.

- Not found: skip the badge; the summary says how to enable GitHub Sponsors.
- Owner is an org or multi-human project: no badge; the summary notes org Sponsors or a fiscal host, with a
  docs link.
- Check can't run at all (no `gh`, no network, auth error): include the badge and flag it unverified. A
  definite not-found is never "can't run".
- The user can opt out. Personal tooling skips it.

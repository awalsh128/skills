# Sponsor badge

Placed after the bullets, on by default, for solo-owner projects. A pink for-the-badge badge linking to the
owner's Sponsors page, with one line of plain text under it:

```markdown
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/sponsors/<owner>)

If you find this project useful, please consider [sponsoring it](https://github.com/sponsors/<owner>) and show
some ❤️ for open source maintainers.
```

Exemplar: https://github.com/agent-sh/agnix. In a centered header (VS Code extensions), put the badge in a
`<p align="center">` block as that README does.

`<owner>` is the git remote owner. Check the page exists with `gh api users/<owner>/sponsorship` (or
`orgs/<owner>/sponsorship`); an HTTP 404, or a fetch of the URL that redirects to the profile page, means no
Sponsors page.

- Not found: skip the badge; the summary says how to enable GitHub Sponsors.
- Owner is an org or multi-human project: no badge; the summary notes org Sponsors or a fiscal host, with a
  docs link.
- Check can't run at all (no `gh`, no network, auth error): include the badge and flag it unverified. A
  definite not-found is never "can't run".
- The user can opt out. Personal tooling skips it.

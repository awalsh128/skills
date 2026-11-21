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

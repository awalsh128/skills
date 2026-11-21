---
name: vsce-project
description:
  Use only when the user says "vsce-project" or explicitly asks for it, to create, change or review the parts
  of a VS Code extension project that are unique to publishing it - package.json manifest identity and listing
  requirements, the Visual Studio Marketplace and Open VSX Registry, the publish job and its credentials, and
  versioning with pre-releases. Not for the extension's own TypeScript (use typescript), general CI (use
  github-cicd), the wording of the README (use create-readme) or editor setup (use project-setup).
---

# vsce-project

Keep a VS Code extension publishable to both registries. The extension is an ordinary TypeScript project; this
skill covers only what differs because it ships through `@vscode/vsce` (the `vsce` command) to the Visual
Studio Marketplace and through `ovsx` to the Open VSX Registry (the registry Cursor, VSCodium and other forks
read). Registry rules change, so when a command or limit matters to the task, confirm it against the tool's
`--help` or the publishing docs instead of relying on this file.

Use typescript for the extension code and github-cicd alongside this one for workflow files.

## Identity

Both registries key an extension on `publisher.name` from `package.json`. The Marketplace adds constraints
that fail late, at publish time, so check them when the manifest is written.

- **`name`**: lowercase, no spaces, unique under the publisher. With `publisher` it forms the extension ID.
- **`displayName`**: unique across the whole Marketplace, even when the ID is unique. Before choosing or
  changing one, search the Marketplace for the exact name and report any collision. If the search fails, say
  the name is unchecked; never assume it is free.
- **`publisher`**: created in the Marketplace management portal and, separately, as a namespace in Open VSX.
  The Marketplace publisher ID cannot be changed after creation. Confirm both exist.
- **Open VSX namespace**: `ovsx create-namespace <publisher>` only makes you a contributor. Ownership needs a
  signed Eclipse publisher agreement (the Eclipse account must list your GitHub username) and a public issue
  in the `EclipseFdn/open-vsx.org` repo. This is a manual one-time step: give the user the checklist and never
  open the issue for them.

## Marketplace requirements

Check these before packaging; the Marketplace rejects or breaks the listing otherwise.

- `icon` is a PNG of at least 128x128 pixels, not an SVG.
- `repository` points at a public repo. `vsce` uses it to rewrite relative README links, and `ovsx` requires
  it unless `--allow-missing-repository` is passed.
- README images use `https` URLs.
- `engines.vscode` is set and matches the APIs the code uses.
- `categories`, `keywords`, `license` and `galleryBanner` are the listing's wording and belong to
  create-readme, not this skill.

## Package contents

A published version cannot be reused, so inspect the `.vsix` before it ships, not after.

- Ship a bundle (esbuild or rollup) rather than `node_modules`, and keep `.vscodeignore` to what the bundle
  needs.
- Run `vsce ls` and check it against an allowlist: the bundle directory, `package.json`, `README`, `LICENSE`,
  `CHANGELOG` and the icon. Fail the job on any other path (tests, source maps, `src`, `node_modules`).

## Versioning

- semantic-release owns the version. Never bump `package.json` by hand: both registries refuse a version that
  exists, so a wrong hand bump blocks the release.
- The Marketplace accepts only `major.minor.patch`. A semver tag such as `1.2.0-rc.1` is rejected.
- Pre-release and release versions must differ, and auto-update installs the highest version, so a pre-release
  must not outrank the next stable. Microsoft's convention is an even minor for releases and an odd minor for
  pre-releases.
- Stable releases come from `main` as usual. A nightly candidate gets a separate `.vsix` version,
  `major.<odd minor>.<run number>`, applied to the package only and never committed:
  `vsce package <version> --no-update-package-json --no-git-tag-version --pre-release`. It is published with
  `--pre-release` on both CLIs. Its git tag (`v1.2.0-rc.1`) then differs from its `.vsix` version, so the
  GitHub prerelease notes state the mapping.
- If a stable release would land on an odd minor it collides with the candidate line; skip to the next even
  minor.

## Deployment

Release and publish are two jobs in the same workflow, not two workflows. A release created with
`GITHUB_TOKEN` does not start another workflow, so a separate `on: release` workflow would silently never run;
github-cicd already releases with tokens that a single workflow can use.

1. **Release job** (semantic-release): in its prepare phase, after the version is known, run `vsce package`
   once, and attach the `.vsix` to the GitHub release as an asset (a GitHub prerelease for a candidate).
   Output whether a release was created and the `.vsix` path, and upload the file as an artifact.
2. **Publish job**: `needs` the release job and runs only when a release was created. It downloads the
   artifact and publishes that same file, so the release asset and both registry copies are identical:
   `vsce publish --packagePath <file>` to the Marketplace, then `ovsx publish <file>`. Add `--pre-release` for
   a candidate. Run the two as independent steps, so one registry's rejection doesn't skip the other, and fail
   the job at the end if either failed. That gives one run's full report.
3. **Credentials** live in a GitHub environment that only the publish job uses, not in the build job.
   - Marketplace: an Azure DevOps personal access token with organization "All accessible organizations" and
     scope Marketplace (Manage), as `VSCE_PAT`. A PAT is a stopgap; the docs also support Entra
     (`vsce publish --azure-credential` with a managed identity), which avoids a long-lived secret.
   - Open VSX: an access token as `OVSX_PAT`. `ovsx` also has `--trusted-publishing`, which exchanges the
     workflow's OIDC token for a short-lived token; prefer it once the repo is registered as a trusted
     publisher.

A half-publish (one registry accepted, the other rejected) has used the version. Do not re-run the job. Either
publish the missing registry by hand from the release asset, or fix the cause and land a releasable commit
(`fix` or `feat`) so semantic-release produces the next version; without one it releases nothing.
`ovsx publish --skip-duplicate` is for an identical re-run, not a way around this.

## Update notice

To tell users when a newer version is published, add the small module in `references/update-notice.md`: one
toast with Update, Dismiss and Never buttons, where Never is stored in a setting. Read it when the user asks
for update messages.

---
name: check-pr-release-type
description:
  Check that a pull request's Conventional Commits title declares the right release type for its diff - feat,
  fix, a non-releasing type, or a breaking change - by mapping each change onto what consumers depend on
  (exports, action inputs and outputs, CLI flags, config keys, defaults, minimum runtime). Use when reviewing
  or about to merge a pull request in a repo that releases from Conventional Commits (semantic-release), when
  the user asks whether a change is breaking or what version it ships as, or says "check-pr-release-type". Not
  for general code review, commit message format (commitlint does that), or release pipeline setup (use
  github-cicd).
---

# check-pr-release-type

With squash merges the pull request title becomes the commit, and the commit decides the release. A wrong type
ships silently: an undeclared breaking change goes out as a minor or patch, and a `chore:` on shipped code
releases nothing. This skill answers one question: does the title's type match what the diff does to
consumers? Linters already check the title's format; this checks its truth.

## Scope beside other reviews

If a general review (a code review skill or command) is also running on this pull request, report only
release-type findings and leave code quality, spec and security to it. If the pull request has a release
preview comment, take the planned version from it instead of computing one.

## Steps

1. **Gather.** `gh pr view <n> --json title,body,baseRefName,files` and `gh pr diff <n>`. Read the release
   config (`release.config.*`, `.releaserc*`, or the `release` key in `package.json`) for custom
   `releaseRules`, and the package directory in a monorepo. Note the body's answer to "Breaking change" if the
   template asks it.
2. **Map the consumer surface.** List what users of this project depend on, for its kind:
   - Library: `exports`, `main`, `types` and the public entry points, exported names and their signatures.
   - GitHub Action: `action.yml` inputs (required, defaults), outputs, `runs.using`.
   - CLI: commands, flags, exit codes, and output other tools parse.
   - Any: config file keys, environment variables, documented defaults and behavior, `engines` and peer
     dependency ranges.
3. **Classify every changed file** against that surface, highest first:
   - **breaking**: removes or renames surface, adds a required input or argument, narrows an accepted type,
     changes a default or documented behavior people rely on, or raises a minimum runtime or peer version.
   - **feature**: adds optional surface (a new export, optional input, flag or output).
   - **fix**: brings behavior back in line with what is documented or clearly intended. `perf` counts here.
   - **none**: internal refactors, tests, docs, CI, dev dependencies.

   A fix that changes behavior some users may depend on is _possibly breaking_: say so, show the change, and
   leave the call to the user.

4. **Compare.** The highest class sets the expected title: breaking → `<type>!:` plus a `BREAKING CHANGE:`
   footer saying what users must change; feature → `feat:`; fix → `fix:` or `perf:`; none → a non-releasing
   type (`chore:`, `refactor:`, `docs:`, `test:`, `ci:`, `build:`). Apply the repo's `releaseRules` where they
   differ. In a monorepo, check the changed paths fall in the package the title's scope names. Check the
   body's breaking change answer agrees too.

Done when every changed file has a class and the title has a verdict.

## Report

Lead with the verdict: **matches**, or **mismatch** with the corrected title. Under it, one line per change
that sets or contradicts the verdict: `file:line`, the surface item it touches, its class. For a breaking
change, include a ready-to-paste footer. Change the title only when the user asks (`gh pr edit <n> --title`).

---
name: check-pr-release-type
description:
  Check that a pull request's Conventional Commits title declares the right release type for its diff - feat,
  fix, a non-releasing type, or a breaking change - by mapping each change onto what consumers depend on. Use
  when reviewing or about to merge a pull request whose title follows Conventional Commits, when the user asks
  whether a change is breaking or what version it ships as, or says "check-pr-release-type". Not for general
  code review, commit message format (commitlint does that), or release pipeline setup (use github-cicd).
---

# check-pr-release-type

With squash merges the pull request title becomes the commit, and the commit decides the release. A wrong type
ships silently: an undeclared breaking change goes out as a minor or patch, and a `chore:` on shipped code
releases nothing. Linters check the title's format; this skill checks its truth: does the type match what the
diff does to consumers?

## Scope beside other reviews

If a general review (a code review skill or command) is also running on this pull request, report only
release-type findings and leave code quality, spec and security to it. If the pull request has a release
preview comment, take the planned version from it instead of computing one.

## Steps

1. **Gather.** `gh pr view <n> --json title,body,baseRefName,files` and `gh pr diff <n>`. Read the release
   config (`release.config.*`, `.releaserc*`, or the `release` key in `package.json`) for custom
   `releaseRules`, and the package directory in a monorepo. With no release config and no tags, the repo
   doesn't release: the title still records what the change means to consumers, so check it the same way and
   say no version is at stake. Note the body's answer to "Breaking change" if the template asks it.
2. **Map the consumer surface**: everything someone outside this repo depends on, for its kind.
   - Library: `exports`, `main`, `types`, the public entry points, exported names and their signatures.
   - GitHub Action: `action.yml` inputs (required, defaults), outputs, `runs.using`.
   - CLI: commands, flags, exit codes, and output other tools parse.
   - Template or config repo: the files and paths other repos copy, set or preset names, and the arguments of
     the scripts that copy them. A workflow or check in a template is surface; this repo's own CI is not.
   - Any: config file keys, environment variables, documented defaults and behavior, checks users run,
     `engines` and peer dependency ranges.
3. **Classify every changed file** against that surface, highest first:
   - **breaking**: removes or renames surface, adds a required input or argument, narrows an accepted type,
     changes a default or documented behavior people rely on, raises a minimum runtime or peer version, or
     makes a check stricter so setups that passed before now fail.
   - **feature**: adds optional surface (a new export, optional input, flag, output, or template file).
   - **fix**: brings behavior back in line with what is documented or clearly intended. `perf` counts here.
   - **none**: internal refactors, tests, docs, this repo's own CI, dev dependencies.

   A change that breaks only some setups (a stricter check most already pass, a fix to behavior a few may rely
   on) is **possibly breaking**: show who it hits and leave the call to the user.

4. **Compare.** The highest class sets the expected title: breaking → `<type>!:` plus a `BREAKING CHANGE:`
   footer saying what users must change; feature → `feat:`; fix → `fix:` or `perf:`; none → a non-releasing
   type (`chore:`, `refactor:`, `docs:`, `test:`, `ci:`, `build:`). Apply the repo's `releaseRules` where they
   differ. In a monorepo, check the changed paths fall in the package the title's scope names. Check the
   body's breaking change answer agrees too.

Done when every changed file has a class and the title has a verdict.

## Report

Lead with the verdict: **matches**, **mismatch** with the corrected title, or **matches, possibly breaking**
with who it hits. Under it, a table with one row per change that sets or contradicts the verdict: `file:line`,
the surface item it touches, its class. For a breaking or possibly breaking change, include a ready-to-paste
footer. Change the title only when the user asks (`gh pr edit <n> --title`).

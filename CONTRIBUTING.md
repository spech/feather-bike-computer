# Contributing

## Work by ticket

Every change should be associated with a ticket. Keep each ticket's work on its
own branch: do not combine unrelated tickets on one branch. If a change grows
beyond the ticket's scope, create or update a ticket and handle it separately.

## Branch workflow

The project has a single long-lived branch, `develop`. All work reaches it
through ticket branches, and releases are cut from it.

1. Start from the latest `develop` branch.
2. Create one branch for the ticket using
   `<type>/<ticket-id>-<short-description>`, for example
   `feature/123-gps-screen` or `fix/456-gpx-parser`. Use lowercase letters and
   hyphens in the description. Supported branch types are `feature`, `fix`,
   `docs`, `test`, `refactor`, `build`, `chore`, and `hotfix`.
3. Make and test the ticket's changes on that branch. Do not commit directly
   to `develop`.
4. Open a pull request from the ticket branch into `develop`, link the ticket,
   and describe the change and how it was tested.
5. Merge the branch into `develop` after review and required checks pass,
   using a squash merge so each ticket lands as one Conventional Commit.
6. To publish a release, merge the release pull request that Release Please
   keeps open against `develop` (see
   [Automated checks and releases](#automated-checks-and-releases)).

If work on `develop` has moved ahead, update the ticket branch from `develop`
before merging, resolving conflicts on the ticket branch.

## Commit messages

All commits must follow the
[Conventional Commits](https://www.conventionalcommits.org/) format:

```text
<type>[optional scope]: <short description>
```

Use an imperative, concise description. Common types include:

- `feat` — add functionality
- `fix` — correct a bug
- `docs` — documentation-only changes
- `test` — add or update tests
- `refactor` — restructure code without changing behavior
- `build` — build or dependency changes
- `chore` — maintenance that does not fit another type

Examples:

```text
feat(gps): add fix status to ride screen
fix(parser): handle empty GPX tracks
docs: describe the ticket branch workflow
```

Use `!` after the type or scope for a breaking change, and include a
`BREAKING CHANGE:` footer when additional explanation is needed.

## Automated checks and releases

GitHub Actions checks ticket branch names on pull requests into `develop`,
each non-merge commit message, and the pull request title. Release Please's own
branch (`release-please--…`) is exempt from the branch-name check. The required
status check is **Check branch, commits, and PR title**.

Each push to `develop` runs Release Please, which creates or updates a release
pull request against `develop` with the generated `CHANGELOG.md` entry and the
next version. Only `feat`, `fix`, and breaking changes produce a new version.
Review and merge the release pull request to tag the version and publish the
GitHub release.

To enforce the workflow, configure GitHub branch protection or a ruleset for
`develop` to require pull requests and the **Check branch, commits, and PR
title** status check before merging. These repository settings cannot be
enabled from workflow files.

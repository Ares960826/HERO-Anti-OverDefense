# Research HERO fork

This fork keeps upstream HERO intact and adds a project-scoped research profile.
It does not change Codex globally. A research repository opts in by materializing
the managed profile into its root `AGENTS.md`.

## Why project scope

Research work needs a specific balance: strong evidence discipline without
letting optional audit machinery displace the scientific question. General
coding projects should retain their own conventions and the host's default
behaviour.

## Install in a research repository

From a checkout of this fork:

```bash
scripts/research-hero install /path/to/research-project
```

The command creates or updates a marked block at the top of the project's
`AGENTS.md`. Existing project instructions are preserved exactly after the
managed block.

No repository URL is loaded at agent runtime. The fork is the maintained source;
the local `AGENTS.md` block is what Codex reads on every project turn. This keeps
the research project usable offline and pins the deployed policy to a reviewable
version.

## Maintain a deployed project

```bash
# Update the managed block to the version in this checkout.
scripts/research-hero update /path/to/research-project

# Exit 0 only when the deployed block is current.
scripts/research-hero check /path/to/research-project

# Remove only the managed block; preserve other AGENTS.md content.
scripts/research-hero remove /path/to/research-project
```

Both `install` and `update` are idempotent. A malformed or duplicated marker is
reported and left untouched for manual review.

## Maintain the fork

- Keep upstream `RULES.md`, `cases/`, and `hosts/` as the general HERO baseline.
- Make research-policy changes in `profiles/RESEARCH.md`.
- Increment the version in the `RESEARCH-HERO:BEGIN` marker when the deployed
  block changes.
- Review the diff, run the tests, and update selected research projects
  explicitly. Do not fetch changing remote rules during an agent run.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The tests cover a new project, preservation of an existing `AGENTS.md`, repeated
installation, profile upgrades, current/outdated checks, malformed markers, and
removal.

# Contributing

## Workflow

1. Create or select an issue with acceptance criteria.
2. Update `main` and create a focused branch, for example
   `lj/feat/12-market-adapter`.
3. Implement the change with tests for meaningful behavior.
4. Run the checks in the README and open a PR linking the issue.
5. Review the diff and passing CI before merging.

Milestone 1 setup PRs may have dependencies. Follow their documented merge order;
the CI PR initially targets the quality/test branch. Retarget it to `main` after
the quality/test PR merges, if GitHub has not already done so.

## Dependencies and configuration

Use `uv add` for runtime dependencies and `uv add --dev` for development tools.
For reviewed upgrades, run `uv lock --upgrade` (or `--upgrade-package NAME`),
then `uv sync` and the checks. Commit the resulting lockfile.

Do not commit secrets, local environments, datasets, or generated distributions.
No environment variables or provider credentials are required for the current
CLI. Add documented safe examples when configuration is introduced.

## Tests

Keep unit tests deterministic and independent of live APIs. Put external-system
tests in `tests/integration/` and mark them `integration`. When those tests are
added, document required services and provision them explicitly in CI. Type
annotate new code and test helpers; strict mypy covers both.

## Repository administration after setup PRs merge

- Keep `main` as the default branch.
- Protect `main` with required checks **Quality, tests, and build** and
  **Dependency audit** after those checks have run successfully on GitHub.
- Require resolved review conversations and disable force pushes and deletion
  of the default branch. Decide reviewer requirements to suit a solo project.
- Confirm Dependabot is enabled for uv and GitHub Actions.
- An AI reviewer is optional. Install its GitHub App separately with access to
  selected repositories and keep its feedback advisory.

Repository settings and third-party app installation are not applied by merging
documentation files; track their completion in the repository setup issue.

# 📦 Release & Versioning Guide

LANSpeed follows **Semantic Versioning** and uses protected, reviewable release branches. The `main` branch is the stable integration branch; feature work must not be committed directly to it.

## Version format

```text
MAJOR.MINOR.PATCH
```

* **MAJOR** — incompatible public API, CLI, or protocol changes.
* **MINOR** — backward-compatible features and improvements.
* **PATCH** — backward-compatible bug fixes and security fixes.

The package version must stay synchronized in both locations:

* `pyproject.toml` → `[project].version`
* `src/lan_speed_tester/__init__.py` → `__version__`

Every release must also have a matching entry in `CHANGELOG.md`.

## Branch naming

Use a dedicated branch for each planned release or focused fix:

| Work | Branch pattern | Example |
| --- | --- | --- |
| Release feature | `feat/vX.Y.Z-short-description` | `feat/v0.2.0-network-diagnostics` |
| Bug fix | `fix/short-description` | `fix/udp-timeout-handling` |
| Documentation | `docs/short-description` | `docs/release-instructions` |

Do not push feature commits directly to `main`.

## Commit messages

Use Conventional Commit-style messages:

```text
feat(udp): add packet-loss diagnostics
fix(server): close UDP socket after bind failure
test(diagnostics): cover percentile calculations
docs(changelog): document v0.2.0
ci: test supported Python versions
```

Keep commits focused so each change can be reviewed and reverted independently.

## Release checklist

Before opening a release pull request:

1. Implement the release scope on its dedicated branch.
2. Add or update automated tests.
3. Run `python -m compileall -q src`.
4. Run `python -m unittest discover -s tests -v`.
5. Verify `python -m lan_speed_tester --version`.
6. Synchronize `pyproject.toml`, `__version__`, `README.md`, and `CHANGELOG.md`.
7. Open a pull request targeting `main` and wait for review and successful CI.

After the pull request is merged:

1. Create an annotated tag on the merged release commit.
2. Use the `v` prefix, for example `v0.2.0`.
3. Publish the GitHub Release using the matching changelog entry.
4. Start the next release branch from the updated `main`.

Do not create a public release tag before the corresponding release has passed review and CI.

## Planned release sequence

| Version | Scope |
| --- | --- |
| `0.2.0` | Network diagnostics: UDP packet loss, RTT jitter, repeated TCP latency, and statistics |
| `0.3.0` | Advanced benchmarking: multi-stream tests, repeat runs, profiles, and live progress |
| `0.4.0` | Reporting and intelligence: local history, comparisons, exports, HTML reports, and interface discovery |

# Changelog

## v2.3.0 — 2026-10-28

### Added

- **`attest: 'true'`** (`mode: manifest`): creates a GitHub artifact attestation with `actions/attest` (pinned v4.2.2) whose subject is the manifest's canonical bytes, so the subject digest is the PRML hash, and whose predicate (`https://falsify.dev/prml/v<version>`) is the PRML bar. Verifiable with `gh attestation verify <canonical-file> --repo <owner/repo> --predicate-type https://falsify.dev/prml/v0.1`, without trusting the registry. New outputs `attestation-url` and `canonical-path`. The calling job needs `id-token: write` and `attestations: write`.
- Self-test job `attestation`: creates a real attestation for a sample manifest and verifies it with `gh attestation verify`.

### Changed

- Default `falsify-version` `0.4.1` → `0.5.0` (adds `falsify anchor`, `falsify receipt verify`, a lockable `falsify init` and `falsify attest --as test-result`).

## v2.2.1 — 2026-10-28

### Changed

- Default `falsify-version` `0.4.0` → `0.4.1`: `mode: manifest` with `observed` now rejects a non-finite observation (`inf`, `nan`) with exit 2 instead of passing every `>=` bar.

## v2.2.0 — 2026-10-28

### Fixed

- **`anchor-to-registry` now works in `mode: manifest`** (and `schema-only`). The anchor step only looked for `.falsify/<claim>/spec.yaml`, so a standalone PRML manifest was never posted and no `permalink` came back. It now anchors `manifest-path` when set, otherwise the engine claim's spec, warns when there is nothing to anchor or the file is missing, and still skips anchoring on tamper.

### Changed

- Default `falsify-version` `0.3.10` → `0.4.0` (needs Python 3.11 or later; the default `python-version` is 3.11).
- README and examples: `@v1` → `@v2` everywhere (the floating `v1` tag points at old code); inputs table now lists `manifest` mode and the `observed` input; new example `examples/manifest-anchor.yml`; the registry description now says what it stores (the manifest under its hash, with an RFC 3161 timestamp and a Rekor entry); spec licence corrected to the Community Specification License 1.0.
- Self-test: installs `falsify==0.4.0` and exercises manifest-mode anchoring against an unreachable registry (best-effort, the step must still pass).

## v2.0.3 — 2026-06-02

### Changed

- README/CONTRIBUTING: updated the conformance-vector count to **21 (13 v0.1 + 8 v0.2)** following the addition of vector TV-013 (integer-valued threshold) to the v0.1 normative suite. Docs only; no input/output or behaviour changes.

## v2.0.2 — 2026-05-31

### Changed

- Default `falsify-version` bumped `0.3.0` → `0.3.1`, so `@v2` installs the PRML CLI that includes the integer-valued `threshold` canonicalization fix (v0.1 threshold renders as float, matching the JS/Go/Rust reference impls). No input/output changes.
- README: corrected stale `falsify-version` references (`0.1.4` → `0.3.1`), updated the Spec status block, and fixed the conformance-vector count (`12` → `20`: 12 v0.1 + 8 v0.2).

## v2.0.1 — 2026-05-31

### Fixed

- **`manifest` / `guard` modes no longer crash on a clean run.** `HASH` / `PERMALINK` were unset in modes that do not anchor to the registry, so the step summary aborted with `unbound variable` under `set -u` even when verification passed. They are now initialised.
- **TAMPER / FAIL results are now reported correctly.** GitHub runs composite `shell: bash` with `-e` (errexit). Because `falsify` returns exit 3 (TAMPER) and 10 (FAIL) by design, the verify line aborted the step before the exit code was captured and mapped, leaving `status=inconclusive`. The script now runs with `set +e -o pipefail` so those codes are mapped to `tamper` / `fail`.

### Security

- Removed `${{ }}` template interpolation from `run:` shell bodies: `falsify-version` now flows through an env var with a semver-format check, and `github.action_path` through an `ACTION_PATH` env var.
- The locked-spec path is passed to `python` via `argv` instead of an f-string, so a claim name cannot break out of the inline script.
- `registry-url` is validated as `https://`, and the registry's returned hash/permalink are validated (hex / https) and stripped of newlines before being written to `$GITHUB_OUTPUT`.
- Pinned `actions/setup-python` to a commit SHA (v6.2.0).

### Added

- End-to-end integration self-test that runs the action via `uses: ./` in `manifest` mode (PASS and TAMPER), which is what surfaced the two fixes above.

### Notes

- No input or output changes. `@v2` consumers pick up these fixes automatically on the next run.

## v2.0.0 — 2026-05-30

### Added

- **`manifest` mode** — verifies a PRML manifest's SHA-256 (hash/tamper) via the `falsify` reference CLI, and evaluates the predicate when `observed` is set. The genuine PRML-manifest verifier (exit 0 PASS · 3 TAMPER · 10 FAIL). Pin with `expected-hash` or commit the `.prml.sha256` sidecar. New `observed` input.

### Changed

- **Default `falsify-version` bumped `0.1.4` → `0.3.0`.** As of falsify 0.3.0 the `falsify` command is the PRML manifest CLI; the pre-registration workflow engine is the `falsify-engine` command (same install).
- The `guard` / `verdict` / `lock` modes now invoke `falsify-engine`, so their behavior is unchanged for existing consumers — the action handles the switch internally.

### Notes

- `guard`/`verdict`/`lock` consumers need no workflow change. To stay on the old 0.1.x layout (where `falsify` *was* the engine), pin `falsify-version: 0.1.4`.

## v1.0.1 — 2026-05-08

### Fixed

- Removed the `hypothesis.schema.yaml` / `examples/template.yaml` curl workaround now that [`falsify` v0.1.4 ships those files inlined](https://pypi.org/project/falsify/0.1.4/) (via `_BUNDLED_SCHEMA_YAML` / `_BUNDLED_TEMPLATE_YAML` constants). `pip install falsify==0.1.4` is now sufficient — no post-install file fetch required.
- Bumped default `falsify-version` from `0.1.3` to `0.1.4`.
- Removed the "falsify v0.1.3 packaging gap" note from README's "Known limitations" section.
- Self-test now exercises the full `falsify install + lock` flow end-to-end (was: CLI-load only).

### Notes

- No breaking changes. Existing `studio-11-co/prml-verify-action@v1` consumers automatically pick up the cleaner install path on the next CI run.

## v1.0.0 — 2026-05-07

Initial release.

- Composite GitHub Action wrapping the `falsify` CLI from PyPI
- Three modes: `guard` (default scan), `verdict` (specific claim), `lock` (one-time pre-registration)
- Optional `anchor-to-registry` POSTs the manifest to `registry.falsify.dev` and emits a paste-ready README badge snippet
- `expected-hash` input pins a specific SHA-256 across CI runs
- Outputs: `hash`, `permalink`, `status`, `badge-snippet`
- GitHub Actions Step Summary surfaces a clean status table per run
- Tracks PRML spec v0.1.3; pinned default `falsify-version: 0.1.3`

## Unreleased / planned

- Allowlist of acceptable status transitions (e.g. block PASS→FAIL on protected branch)
- Optional Sigstore wrapping of the registry POST for identity-attested receipts
- Native `falsify-version: latest` resolution against PyPI
- v0.2 spec compatibility (RFC freeze 2026-05-22)

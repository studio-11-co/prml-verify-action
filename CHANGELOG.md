# Changelog

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

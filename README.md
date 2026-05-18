# PRML Verify — GitHub Action

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20177839.svg)](https://doi.org/10.5281/zenodo.20177839)

[![PRML locked · 04fa1689ac55](https://registry.falsify.dev/badge/04fa1689ac552fb1f7c3eaf9d0f6c2c0e8c1ca9d4ab6d2fb91a5e7df2c9b62f3.svg)](https://registry.falsify.dev/04fa1689ac552fb1f7c3eaf9d0f6c2c0e8c1ca9d4ab6d2fb91a5e7df2c9b62f3)

> Verify [PRML](https://spec.falsify.dev/v0.1) (Pre-Registered ML Manifest) commitments in CI. Block merges when an evaluation claim was tampered, regressed below threshold, or never locked. Optionally anchor the hash to the public registry.

[![60-second PRML walkthrough — paste, lock, receipt, badge](https://spec.falsify.dev/demo/demo.gif)](https://spec.falsify.dev/demo/)

**TL;DR — drop this in your workflow:**

```yaml
- uses: studio-11-co/prml-verify-action@v1
```

If `.falsify/` exists in your repo, this will fail the build on any tampered or regressed claim. That's it. The defaults are sane for most CI setups.

---

## What this does

[PRML](https://spec.falsify.dev/v0.1) is a small open spec (CC BY 4.0) for committing an ML evaluation claim — metric, threshold, dataset split, model version — to a SHA-256 hash **before** the run. The hash is a tamper-evident receipt anyone can re-derive against the canonical bytes.

This Action wraps the [`falsify`](https://github.com/studio-11-co/falsify) reference CLI as a composite GitHub Action. Three modes:

| Mode | What it does | Exit codes |
|---|---|---|
| `guard` (default) | Scans every claim under `.falsify/`. Fails if any is FAIL or STALE. Use as a CI gate. | 0 PASS · 10 FAIL · 3 TAMPER |
| `verdict` | Checks one specific claim by name. | 0 PASS · 10 FAIL · 3 TAMPER |
| `lock` | Hashes and freezes a claim. Rare in CI — usually a one-time pre-registration step run locally before the experiment. | 0 |
| `schema-only` | Validates a PRML YAML against the v0.1 / v0.2-RFC JSON Schema (no `.falsify/` tree required, no lock needed). For repos that ship a single canonical manifest at a known path. | 0 PASS · 10 FAIL · 2 IO |

It can also optionally **POST your manifest to [registry.falsify.dev](https://registry.falsify.dev)** so the receipt is publicly re-derivable from a permalink (with a README badge).

---

## Why use this

- **Block post-hoc threshold tuning at merge time.** If someone edits the locked manifest after the experiment ran, the hash changes and CI fails with exit code 3.
- **Make eval claims falsifiable.** A reviewer or regulator who reads your paper or model card can re-derive the SHA-256 from the canonical bytes and confirm the threshold was fixed before the data.
- **Five-line integration.** No service to deploy, no account to register. The Action runs `falsify` from PyPI; the optional registry is content-addressed and stateless beyond the hash.

What this does **not** solve, named explicitly in §8.1 of the spec: selective non-publication. You can pre-register ten claims and report two. PRML is a commitment primitive, not a complete publication-integrity system.

---

## Quickstart

### 1. Lock a claim locally (one-time, before CI)

```bash
pip install falsify
falsify init my-accuracy-claim     # creates .falsify/my-accuracy-claim/spec.yaml
# edit spec.yaml: metric, threshold, dataset_split, model_version, claim, submitter
falsify lock my-accuracy-claim     # hashes the canonical bytes
```

Commit the resulting `.falsify/` directory to your repo.

### 2. Add the Action to your workflow

```yaml
# .github/workflows/prml.yml
name: PRML
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: studio-11-co/prml-verify-action@v1
```

That's it. Now any commit that tampers with a locked claim, or any model-version drift that pushes the metric below the threshold, fails the build.

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `mode` | no | `guard` | `guard` / `verdict` / `lock` / `schema-only` |
| `claim` | when `mode=verdict` or `mode=lock` | `` | Claim name |
| `manifest-path` | when `mode=schema-only` | `` | Path to manifest YAML to schema-validate |
| `schema-version` | no | `v0.1` | `v0.1` (stable) or `v0.2-rfc` (open through 2026-05-22) |
| `expected-hash` | no | `` | Pin a SHA-256 hash; mismatch → exit 3 |
| `anchor-to-registry` | no | `false` | If `true`, POST manifest to `registry-url` and emit `permalink` |
| `registry-url` | no | `https://registry.falsify.dev` | Registry endpoint |
| `registry-handle` | no | repo owner | Submitter handle on the registry commit |
| `python-version` | no | `3.11` | Python version |
| `falsify-version` | no | `0.1.4` | falsify package version |
| `working-directory` | no | `.` | Path containing `.falsify/` |

## Outputs

| Output | Description |
|---|---|
| `hash` | SHA-256 digest of the canonical manifest bytes |
| `permalink` | Registry permalink (only when `anchor-to-registry=true` succeeded) |
| `status` | Final status: `pass` / `fail` / `tamper` / `inconclusive` |
| `badge-snippet` | Markdown snippet for embedding the registry badge in your README |

---

## Examples

### Basic (zero-config CI gate)

```yaml
- uses: actions/checkout@v4
- uses: studio-11-co/prml-verify-action@v1
```

### Verdict for a specific claim with hash pinning

```yaml
- uses: actions/checkout@v4
- uses: studio-11-co/prml-verify-action@v1
  with:
    mode: verdict
    claim: imagenet-resnet50-baseline
    expected-hash: fb7403c40afe63d892bf4aea2c123fdd7fe85366b74a277875465c4cb3cbf19c
```

### Schema-only mode (no `.falsify/` tree, single canonical manifest)

For repos that ship one PRML manifest at a known path and only want a schema-shape check in CI:

```yaml
- uses: actions/checkout@v6
- uses: studio-11-co/prml-verify-action@v1
  with:
    mode: schema-only
    manifest-path: claims/cv-screening.prml.yaml
    schema-version: v0.1
```

Exit codes: `0` PASS, `10` schema validation FAIL, `2` IO / bad inputs. Works against the live JSON Schemas at `https://spec.falsify.dev/schema/` (the same ones merged into the SchemaStore catalog).

### Anchor a verified claim to the public registry, surface a README badge

```yaml
- uses: actions/checkout@v4
- id: prml
  uses: studio-11-co/prml-verify-action@v1
  with:
    mode: verdict
    claim: imagenet-resnet50-baseline
    anchor-to-registry: 'true'
- name: Show badge snippet
  run: echo "${{ steps.prml.outputs.badge-snippet }}"
```

The `badge-snippet` output is a paste-ready Markdown string like:
```markdown
[![PRML locked · fb7403c40afe](https://registry.falsify.dev/badge/<hash>.svg)](https://registry.falsify.dev/<hash>)
```

### Verify and fail-fast on regression in a model release pipeline

```yaml
- uses: actions/checkout@v4
- uses: studio-11-co/prml-verify-action@v1
  with:
    mode: guard
    falsify-version: 0.1.4
- run: ./deploy-to-prod.sh
  if: steps.prml.outputs.status == 'pass'
```

More examples in the [`examples/`](examples/) directory.

---

## How it integrates with `registry.falsify.dev`

When `anchor-to-registry: 'true'`:

1. The Action POSTs the canonical manifest YAML to `${registry-url}/commit`
2. The registry recomputes SHA-256 over the same canonical bytes
3. The registry returns `{hash, permalink, timestamp}` and stores the manifest publicly
4. The Action emits the `permalink` and a paste-ready `badge-snippet` output

The registry has no auth and no server-side state beyond the hash. It exists for discoverability — your manifest can be anchored anywhere (a public git repo, an arXiv preprint, a Sigstore attestation, your own static host). The registry is one option, not a requirement.

Read more: [What is PRML?](https://falsify.dev/what-is-prml) · [PRML vs in-toto, SLSA, Model Cards, HELM](https://falsify.dev/vs)

---

## Also see

If your workflow already runs through MLflow, `prml-verify-action` pairs well with [`mlflow-falsify`](https://pypi.org/project/mlflow-falsify/) — a tiny MLflow Run Context Provider plugin (`pip install mlflow-falsify`) that auto-tags every `mlflow.start_run()` with the PRML manifest hash plus the metric, comparator, threshold, and dataset id. Zero workflow change required. Source: [`studio-11-co/mlflow-falsify`](https://github.com/studio-11-co/mlflow-falsify).

For the JavaScript / Node.js side of the same canonicalization: [`falsify-js`](https://www.npmjs.com/package/falsify-js) on npm.

For execution-integrity beyond what PRML §8.1 covers, pair this action with [`cosign`](https://docs.sigstore.dev/cosign/) — the cookbook walks through it as [Pattern 11: PRML + Sigstore](https://github.com/studio-11-co/falsify-cookbook/blob/main/patterns/11-sigstore-execution.md).

## Audit & compliance crosswalks

Subcategory-by-subcategory maps from major AI governance frameworks to PRML fields (FULL / PARTIAL / NONE tagged):

- [EU AI Act Article 12](https://spec.falsify.dev/eu-ai-act/article-12/) — code-level pattern for the 2 August 2026 high-risk deadline
- [NIST AI RMF 1.0](https://spec.falsify.dev/nist-ai-rmf/) — GOVERN / MAP / MEASURE / MANAGE subcategory map
- [ISO/IEC 42001:2023](https://spec.falsify.dev/iso-42001/) — AI Management System clause-by-clause evidence map

---

## Spec status

- v0.1.4 stable release (PRML v0.1 specification)
- v0.2 RFC freeze: 2026-05-22
- Spec license: CC BY 4.0
- Reference implementations: Python · JavaScript · Go · Rust (byte-equivalent across 12 conformance vectors)

If you find a gap or edge case the spec doesn't handle, [open an issue](https://github.com/studio-11-co/falsify/issues) before the freeze date — that's how v0.2 gets sharper.

---

## Known limitations

- **Spec format dual-track.** The PRML manifest format described at [spec.falsify.dev/v0.1](https://spec.falsify.dev/v0.1) (8 YAML fields, content-addressed) and the `falsify` CLI's internal `hypothesis.schema.yaml` (claim / falsification / experiment) are currently distinct. The reconciliation work is part of the v0.2 RFC freeze (2026-05-22). Until then, use the PRML format for registry commits and the hypothesis schema for `falsify lock` flows.

## License

This Action is MIT-licensed. The PRML specification is CC BY 4.0. The reference [`falsify`](https://github.com/studio-11-co/falsify) toolkit is MIT.

Maintained by [Studio 11](https://falsify.dev) · PRML / falsify track lead: [Cüneyt Öztürk](https://www.linkedin.com/in/cuneyt-ozturk-39812963/) · `hello@studio-11.co`


---

## Status

- v0.1 stable. v0.2 RFC open through 2026-05-22 — [spec.falsify.dev/v0.2-rfc](https://spec.falsify.dev/v0.2-rfc).
- The PRML JSON Schema is in the [SchemaStore catalog](https://www.schemastore.org/json/) (merged 2026-05-11), so `*.prml.yaml` files autocomplete in VS Code, JetBrains, Helix, Zed, and Cursor out of the box.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) and the [`good first issue`](https://github.com/studio-11-co/prml-verify-action/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) label for scoped work.

**Cite the spec:** Öztürk, C. (2026). *PRML v0.1*. Zenodo. [https://doi.org/10.5281/zenodo.20177839](https://doi.org/10.5281/zenodo.20177839)

# PRML Verify — GitHub Action

[![PRML locked · 04fa1689ac55](https://registry.falsify.dev/badge/04fa1689ac552fb1f7c3eaf9d0f6c2c0e8c1ca9d4ab6d2fb91a5e7df2c9b62f3.svg)](https://registry.falsify.dev/04fa1689ac552fb1f7c3eaf9d0f6c2c0e8c1ca9d4ab6d2fb91a5e7df2c9b62f3)

> Verify [PRML](https://spec.falsify.dev/v0.1) (Pre-Registered ML Manifest) commitments in CI. Block merges when an evaluation claim was tampered, regressed below threshold, or never locked. Optionally anchor the hash to the public registry.

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
| `mode` | no | `guard` | `guard` / `verdict` / `lock` |
| `claim` | when `mode=verdict` or `mode=lock` | `` | Claim name |
| `expected-hash` | no | `` | Pin a SHA-256 hash; mismatch → exit 3 |
| `anchor-to-registry` | no | `false` | If `true`, POST manifest to `registry-url` and emit `permalink` |
| `registry-url` | no | `https://registry.falsify.dev` | Registry endpoint |
| `registry-handle` | no | repo owner | Submitter handle on the registry commit |
| `python-version` | no | `3.11` | Python version |
| `falsify-version` | no | `0.1.3` | falsify package version |
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
    falsify-version: 0.1.3
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

## Spec status

- v0.1.3 working draft, public review
- v0.2 RFC freeze: 2026-05-22
- Spec license: CC BY 4.0
- Reference implementations: Python · JavaScript · Go · Rust (byte-equivalent across 12 conformance vectors)

If you find a gap or edge case the spec doesn't handle, [open an issue](https://github.com/studio-11-co/falsify/issues) before the freeze date — that's how v0.2 gets sharper.

---

## Known limitations

- **`falsify` v0.1.3 packaging gap.** The PyPI wheel for `falsify==0.1.3` omits two bundled data files (`hypothesis.schema.yaml`, `examples/template.yaml`) because `pyproject.toml` does not declare them as `package-data`. Both `falsify lock` and `falsify init` fail with `FileNotFoundError` on a clean install. This Action ships a workaround that fetches the missing files from the matching git tag at install time. The workaround will be removed when `falsify` v0.1.4 ships with proper packaging metadata. Track: [studio-11-co/falsify#packaging](https://github.com/studio-11-co/falsify/issues).
- **Spec format dual-track.** The PRML manifest format described at [spec.falsify.dev/v0.1](https://spec.falsify.dev/v0.1) (8 YAML fields, content-addressed) and the `falsify` CLI's internal `hypothesis.schema.yaml` (claim / falsification / experiment) are currently distinct. The reconciliation work is part of the v0.2 RFC freeze (2026-05-22). Until then, use the PRML format for registry commits and the hypothesis schema for `falsify lock` flows.

## License

This Action is MIT-licensed. The PRML specification is CC BY 4.0. The reference [`falsify`](https://github.com/studio-11-co/falsify) toolkit is MIT.

Maintained by [Studio 11](https://falsify.dev) · PRML / falsify track lead: [Cüneyt Öztürk](https://www.linkedin.com/in/cuneyt-ozturk-39812963/) · `hello@studio-11.co`

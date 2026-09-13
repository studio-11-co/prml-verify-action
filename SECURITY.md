# Security Policy — prml-verify-action (GitHub Action)

## Reporting a vulnerability

Email **hello@falsify.dev** with the subject prefix `[SECURITY]`. Include a
description, the affected component and version, and a reproduction if you have
one. We aim to acknowledge within 3 working days and to say, within 10, whether
we consider it a vulnerability and what we intend to do. Do not open a public
issue for a suspected vulnerability.

There is no bug bounty. Credit is given in the changelog if you want it.

## Supported versions

| Version | Supported |
|---|---|
| `v2` (floating) and `v2.x` | yes |
| `v1` | no |

## Trust model

The action runs `falsify verify` (and, in `manifest` mode, `falsify lock`/`hash`)
against files in the checked-out repository. Those verbs only read, canonicalize,
hash and compare; a manifest is never executed. The action does **not** run the
workflow engine (`falsify-engine run`/`replay`), which would execute code from a
spec and is unsafe on untrusted input by design.

Because it runs in your CI, apply the usual Actions hygiene: pin the action by
commit SHA rather than a floating tag if your threat model includes tag
re-pointing, and grant the job the minimum `permissions:`. The action needs no
secrets and requests none.

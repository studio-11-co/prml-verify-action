#!/usr/bin/env python3
"""Anchor a PRML manifest to the public registry.

Usage:
    python anchor.py <manifest_path> <registry_url> <handle>

Reads the YAML manifest, POSTs it to <registry_url>/commit, prints
NEWLINE-separated key=value lines (hash, permalink) on success.
Silent on failure (exit 0 either way — registry POST is best-effort).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: anchor.py <manifest_path> <registry_url> <handle>", file=sys.stderr)
        return 2

    manifest_path, registry_url, handle = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            yaml_content = fh.read()
    except OSError as e:
        print(f"err: cannot read manifest {manifest_path}: {e}", file=sys.stderr)
        return 0  # best-effort

    payload = json.dumps({"yaml": yaml_content, "handle": handle}).encode("utf-8")
    req = urllib.request.Request(
        f"{registry_url.rstrip('/')}/commit",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"err: registry HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"err: registry request failed: {e}", file=sys.stderr)
        return 0

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(f"err: non-JSON registry response: {body[:200]}", file=sys.stderr)
        return 0

    h = data.get("hash", "")
    permalink = data.get("permalink", "")
    if h:
        print(f"hash={h}")
    if permalink:
        print(f"permalink={permalink}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

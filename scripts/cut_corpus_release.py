#!/usr/bin/env python3
"""Cut a witnessed corpus release for this repository.

This is the producer side of `receipt verify`, scoped deliberately to this one
lane. It is NOT the generic producer-side chain cutter — that belongs to
TheAxiomFoundation/receipt#7, which will build one record schema and one cutter
for every consumer (encoder generation records, the Brier proposer, this
corpus). Until that lands, a lane that wants a verifiable corpus needs its own
cutter, and duplicating it here on purpose is cheaper than pre-committing the
generic design to this lane's shape.

What one cut does:

1. Enumerate the content files (`nz/**/*.yaml`) and the attested files the
   verification spec requires, and record each by SHA-256.
2. Append those rows, plus the gate declarations, to the append-only journal.
   An existing journal is only ever extended: rows already witnessed are
   reproduced byte for byte, and a changed file appends a new row rather than
   rewriting the old one.
3. Cut the next release manifest over the journal, sign it with the corpus
   custody key, and obtain two independent RFC 3161 timestamp tokens.
4. Verify the whole chain, and the corpus binding, before anything is written
   into the repository.

Step 4 is the point. The cutter stages everything in a temporary directory and
runs the same `receipt` verification an outside auditor runs; if that refuses,
nothing lands.

    python scripts/cut_corpus_release.py --private-key <path> [--dry-run]

The private key is read from a path outside the repository and is never
written, logged, or echoed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from typing import Any

from receipt.canonical import canonical_bytes
from receipt.corpus import verify_corpus_binding
from receipt.release_chain import (
    ReleaseChainError,
    manifest_filename,
    verify_release_chain,
)
from receipt.sign import sign_payload, spki_sha256

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from verification.spec import (  # noqa: E402
    ATTESTED_PATHS,
    CHAIN,
    CORPUS,
    GATE_DECLARATIONS_RELATIVE,
    JOURNAL_SCHEMA,
    SPEC,
)

TSA_ENDPOINTS = {
    "freetsa": "https://freetsa.org/tsr",
    # DigiCert's documented RFC 3161 endpoint is plain HTTP; their TLS endpoint
    # does not answer timestamp queries. The token is a self-authenticating
    # signature verified against the pinned root, so the transport is not the
    # trust boundary.
    "digicert": "http://timestamp.digicert.com",
}
MAX_TOKEN_BYTES = 1024 * 1024
TIMEOUT_SECONDS = 45.0


class CutError(RuntimeError):
    """The release could not be built, or refused its own verification."""


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def content_paths(root: pathlib.Path) -> list[str]:
    found: list[str] = []
    for content_root in CORPUS.content_roots:
        base = root / content_root
        for candidate in sorted(base.rglob("*")):
            if candidate.is_symlink() or not candidate.is_file():
                continue
            relative = candidate.relative_to(root).as_posix()
            if CORPUS.is_content_path(relative):
                found.append(relative)
    return sorted(found)


def load_existing_rows(journal: pathlib.Path) -> list[dict[str, Any]]:
    if not journal.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in journal.read_bytes().decode("utf-8").split("\n")[:-1]:
        rows.append(json.loads(line))
    return rows


def effective_view(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Latest digest per path across every file row, present or removed."""

    view: dict[str, str] = {}
    for row in rows:
        if row.get("kind") not in ("content", "attested"):
            continue
        if row["state"] == "present":
            view[row["path"]] = row["sha256"]
        else:
            view.pop(row["path"], None)
    return view


def declared_gate_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {row["gateId"] for row in rows if row.get("kind") == "gate"}


def build_rows(root: pathlib.Path, existing: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the rows to APPEND. Never rewrites an existing row."""

    view = effective_view(existing)
    index = len(existing)
    appended: list[dict[str, Any]] = []

    def row(kind: str, path: str, digest: str, state: str) -> dict[str, Any]:
        nonlocal index
        entry = {
            "schemaVersion": JOURNAL_SCHEMA,
            "entryIndex": index,
            "kind": kind,
            "path": path,
            "sha256": digest,
            "state": state,
        }
        index += 1
        return entry

    present_content = content_paths(root)
    for relative in present_content:
        digest = sha256_file(root / relative)
        if view.get(relative) != digest:
            appended.append(row("content", relative, digest, "present"))

    for relative in sorted(ATTESTED_PATHS):
        path = root / relative
        if not path.is_file():
            raise CutError(f"the spec requires an attested path that is absent: {relative}")
        digest = sha256_file(path)
        if view.get(relative) != digest:
            appended.append(row("attested", relative, digest, "present"))

    # A content file that vanished from the tree is recorded as removed, so the
    # closed-world sweep still matches and the deletion stays visible in the
    # witnessed history rather than becoming an absence.
    known_content = {
        r["path"] for r in existing if r.get("kind") == "content"
    }
    for relative in sorted(known_content - set(present_content)):
        if relative in view:
            appended.append(row("content", relative, view[relative], "removed"))

    gates = json.loads((root / GATE_DECLARATIONS_RELATIVE).read_text())
    already = declared_gate_ids(existing)
    for gate in gates:
        if gate["gateId"] in already:
            continue
        entry = {
            "schemaVersion": JOURNAL_SCHEMA,
            "entryIndex": index,
            "kind": "gate",
            "gateId": gate["gateId"],
            "tier": gate["tier"],
            "outcome": gate["outcome"],
            "evidence": gate["evidence"],
        }
        index += 1
        appended.append(entry)

    return appended


def request_timestamp(endpoint: str, query: bytes) -> bytes:
    if endpoint not in TSA_ENDPOINTS.values():
        raise CutError(f"refusing unapproved TSA endpoint: {endpoint!r}")
    request = urllib.request.Request(
        endpoint,
        data=query,
        headers={
            "Content-Type": "application/timestamp-query",
            "Accept": "application/timestamp-reply",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = response.read(MAX_TOKEN_BYTES + 1)
    if not payload:
        raise CutError(f"empty RFC 3161 response from {endpoint}")
    if len(payload) > MAX_TOKEN_BYTES:
        raise CutError(f"oversized RFC 3161 response from {endpoint}")
    return payload


def _git_branch() -> str:
    """The branch this cut actually happened on — recorded, not asserted."""

    completed = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    branch = completed.stdout.strip()
    if completed.returncode != 0 or not branch or branch == "HEAD":
        raise CutError(
            "cannot determine the current git branch for producer provenance"
        )
    return branch


def stamp(digest: str, workspace: pathlib.Path, name: str) -> bytes:
    query = workspace / f"{name}.tsq"
    completed = subprocess.run(
        ["openssl", "ts", "-query", "-digest", digest, "-sha256", "-cert",
         "-out", str(query)],
        check=False, capture_output=True,
    )
    if completed.returncode != 0:
        raise CutError(
            f"openssl ts -query failed: {completed.stderr.decode('utf-8', 'replace')}"
        )
    return request_timestamp(TSA_ENDPOINTS[name], query.read_bytes())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--private-key",
        required=True,
        type=pathlib.Path,
        help="PEM Ed25519 corpus custody private key, outside the repository",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="build and verify the release, then discard it",
    )
    args = parser.parse_args(argv)

    # The custody key must live outside the repository. Nothing downstream
    # enforces this: copytree would duplicate an in-repo key into staging,
    # .pem is an allowed extension under verification/releases/, and a later
    # `git add -A` would publish it with verification still green. Refuse the
    # operator error rather than document against it.
    key_path = args.private_key.resolve()
    if key_path.is_relative_to(ROOT):
        raise CutError(
            "refusing to sign with a private key inside the repository "
            f"({key_path.relative_to(ROOT)}): move it outside the working tree "
            "so it cannot be staged, copied, or committed"
        )
    private_pem = key_path.read_bytes()
    public_key_path = ROOT / CHAIN.anchor_relative / CHAIN.producer_public_key_filename
    if not public_key_path.is_file():
        raise CutError(f"committed producer public key is absent: {public_key_path}")
    actual_spki = spki_sha256(public_key_path.read_bytes())
    if actual_spki != CHAIN.producer_spki_sha256:
        raise CutError(
            "the committed producer public key does not match the SPKI pinned "
            f"in verification/spec.py: {actual_spki} != {CHAIN.producer_spki_sha256}"
        )

    journal_path = ROOT / CHAIN.state_relative
    existing_raw = journal_path.read_bytes() if journal_path.is_file() else b""
    existing = load_existing_rows(journal_path)
    appended = build_rows(ROOT, existing)
    if not appended:
        print("corpus is already fully witnessed at this state; nothing to cut.")
        return 0

    # Splice exact bytes: already-witnessed rows are carried forward verbatim,
    # never re-serialized, so byte preservation holds by construction rather
    # than by a parse/canonicalize round-trip happening to be stable.
    journal_bytes = existing_raw + b"".join(
        canonical_bytes(row) + b"\n" for row in appended
    )
    lines = journal_bytes.decode("utf-8").split("\n")[:-1]

    # The immutable prefix is sealed ONCE, at genesis, over the rows that
    # existed then — and never changes again. Every manifest records the same
    # prefix digest, and the chain verifier requires all of them to agree with
    # the file on disk, so a prefix that grew with each cut would invalidate
    # every earlier release the moment a second one was written.
    prefix_path = ROOT / CHAIN.prefix_relative
    if prefix_path.is_file():
        prefix_bytes = prefix_path.read_bytes()
    else:
        prefix = {
            "schemaVersion": "axiom/rulespec-corpus-prefix/v1",
            "prefixLineCount": len(lines),
            "lineSha256s": [
                hashlib.sha256(line.encode("utf-8")).hexdigest() for line in lines
            ],
            "prefixSha256": hashlib.sha256(
                ("\n".join(lines) + "\n").encode("utf-8")
            ).hexdigest(),
        }
        prefix_bytes = canonical_bytes(prefix) + b"\n"

    release_index = len(list((ROOT / CHAIN.manifest_relative).glob("*.json")))
    previous_digest = None
    if release_index:
        previous = sorted((ROOT / CHAIN.manifest_relative).glob("*.json"))[-1]
        previous_digest = hashlib.sha256(previous.read_bytes()).hexdigest()

    manifest: dict[str, Any] = {
        "schemaVersion": CHAIN.schema_version,
        "releaseIndex": release_index,
        "previousManifestSha256": previous_digest,
        "state": {
            "path": CHAIN.state_path,
            "jsonlSha256": hashlib.sha256(journal_bytes).hexdigest(),
            "lineCount": len(lines),
            "immutablePrefixSha256": hashlib.sha256(prefix_bytes).hexdigest(),
        },
        "append": None
        if release_index == 0
        else {
            "previousLineCount": len(existing),
            "appendedRowCount": len(appended),
            "appendedBytesSha256": hashlib.sha256(
                "".join(f"{line}\n" for line in lines[len(existing):]).encode("utf-8")
            ).hexdigest(),
        },
        "createdAtUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "producer": {
            "repo": "TheAxiomFoundation/rulespec-nz",
            "branch": _git_branch(),
        },
    }
    manifest_bytes = canonical_bytes(manifest) + b"\n"
    manifest_digest = hashlib.sha256(manifest_bytes).hexdigest()
    stem = manifest_filename(release_index, manifest_bytes).removesuffix(".json")

    print(f"release {release_index}: {len(appended)} new row(s), "
          f"{len(lines)} total; manifest {manifest_digest[:16]}…")

    with tempfile.TemporaryDirectory(prefix="nz-corpus-cut-") as name:
        workspace = pathlib.Path(name)
        staging = workspace / "repo"
        # Stage a full copy of the tracked tree so verification runs against a
        # real repository layout, not a hand-assembled subset.
        shutil.copytree(
            ROOT, staging,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache",
                                          ".ruff_cache", ".pixi", "_worktrees"),
            symlinks=True,
        )
        (staging / CHAIN.state_relative).parent.mkdir(parents=True, exist_ok=True)
        (staging / CHAIN.state_relative).write_bytes(journal_bytes)
        (staging / CHAIN.prefix_relative).write_bytes(prefix_bytes)
        manifests = staging / CHAIN.manifest_relative
        manifests.mkdir(parents=True, exist_ok=True)
        (manifests / f"{stem}.json").write_bytes(manifest_bytes)
        (manifests / f"{stem}.producer.sig").write_bytes(
            sign_payload(private_pem, manifest_bytes, domain=b"")
        )
        del private_pem

        for anchor in sorted(CHAIN.anchors):
            print(f"  requesting RFC 3161 token from {anchor}…")
            token = stamp(manifest_digest, workspace, anchor)
            (manifests / f"{stem}.{anchor}.tsr").write_bytes(token)

        print("  verifying the staged release exactly as an auditor would…")
        try:
            verification = verify_release_chain(
                staging, spec=CHAIN, require_chain=True, verify_state=True
            )
            binding = verify_corpus_binding(staging, journal_bytes, spec=CORPUS)
        except (OSError, ReleaseChainError, ValueError) as exc:
            raise CutError(f"the staged release does not verify; nothing written: {exc}")

        head = verification.releases[-1]
        witnesses = ", ".join(
            f"{k}={v.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            for k, v in sorted(head.receipt_times.items())
        )
        print(f"  OK: {len(verification.releases)} release(s), {witnesses}")
        print(f"  OK: {len(binding.content)} content + {len(binding.attested)} "
              f"attested files bound, {len(binding.gates)} gate declaration(s)")

        if args.dry_run:
            print("dry run: discarding the staged release.")
            return 0

        journal_path.parent.mkdir(parents=True, exist_ok=True)
        journal_path.write_bytes(journal_bytes)
        (ROOT / CHAIN.prefix_relative).write_bytes(prefix_bytes)
        destination = ROOT / CHAIN.manifest_relative
        destination.mkdir(parents=True, exist_ok=True)
        for suffix in (".json", ".producer.sig", *[f".{a}.tsr" for a in sorted(CHAIN.anchors)]):
            shutil.copy2(manifests / f"{stem}{suffix}", destination / f"{stem}{suffix}")

    print(f"wrote release {release_index} ({stem}).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CutError as exc:
        print(f"cut_corpus_release: {exc}", file=sys.stderr)
        raise SystemExit(1)

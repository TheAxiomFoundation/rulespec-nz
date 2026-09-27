"""Trust anchors for `receipt verify`, pinned in this repository's own code.

This module is the entire trust configuration for verifying the published NZ
corpus. There is nowhere else for an anchor to live: the `receipt` package
ships machinery and no defaults, so every fingerprint, root digest, policy OID,
content root, and accepted reproducibility tier below is a decision this
repository makes and commits.

That inversion is the point. If the producer could supply these values at run
time — from a workflow variable, an environment variable, a fetched config —
then a producer who wanted to publish something else could simply supply
different anchors along with it, and the verdict would follow. Because they are
here, in the tree the auditor cloned, changing one is a reviewed diff.

An auditor should read this file before trusting any verdict produced with it.
It is deliberately short and contains no logic. `receipt verify` prints this
file's own SHA-256 alongside the verdict so a specific configuration can be
quoted and re-pinned later.

    python -m receipt.cli verify --spec verification/spec.py

See VERIFY.md for the full third-party procedure and for what a passing verdict
does and does not establish.
"""

import pathlib

from receipt.corpus import CorpusSpec
from receipt.release_chain import AnchorSpec, ChainSpec
from receipt.verify import VerificationSpec

#: Journal row schema. A row carrying any other value is refused, so this
#: corpus's rows can never be replayed into another consumer's journal.
JOURNAL_SCHEMA = "axiom/rulespec-corpus-journal/v1"

#: Release manifest schema, likewise namespaced to this corpus. It is inside
#: the canonical bytes the producer key signs, so a manifest signed for this
#: corpus cannot be presented as a manifest for a different one.
MANIFEST_SCHEMA = "axiom_rulespec_corpus_release_v1"

GATE_DECLARATIONS_RELATIVE = "verification/gate-declarations.json"

#: Files outside the swept content roots whose exact bytes the corpus binds.
#: Each one changes what a rule file MEANS or how it was checked: the corpus
#: release the encodings resolve against, the layout contract the closed-world
#: sweep relies on, the pinned validation workflow, both ratchets, and the gate
#: declarations themselves.
ATTESTED_PATHS = frozenset(
    {
        ".axiom/toolchain.toml",
        ".axiom/repository-structure.yaml",
        ".github/workflows/repository-checks.yml",
        "known-validation-gaps.yaml",
        "known-missing-money-atoms.yaml",
        GATE_DECLARATIONS_RELATIVE,
        # The auditor's own instructions are witnessed too: a tampered VERIFY.md
        # could talk a reader out of checking the thing it documents.
        "VERIFY.md",
    }
)

CHAIN = ChainSpec(
    manifest_relative=pathlib.PurePosixPath("verification/releases/manifests"),
    state_relative=pathlib.PurePosixPath("verification/corpus-journal.jsonl"),
    prefix_relative=pathlib.PurePosixPath("verification/immutable-prefix.json"),
    anchor_relative=pathlib.PurePosixPath("verification/releases/anchors"),
    release_root_relative=pathlib.PurePosixPath("verification/releases"),
    schema_version=MANIFEST_SCHEMA,
    producer_public_key_filename="corpus-custody-ed25519.pub",
    # SHA-256 of the DER SubjectPublicKeyInfo of the corpus custody key. The
    # committed .pub file is checked against this on every run, so replacing
    # the key file alone changes nothing.
    producer_spki_sha256=(
        "f703c8d871f444cd40a7871d4de066f263aba46abb6ee99003378bb102859f07"
    ),
    anchors={
        # Two timestamp authorities with no common operator, so one compromised
        # or coerced authority cannot move a release's witnessed time alone.
        # Every value is pinned independently: the root certificate bytes, the
        # policy OID the token must assert, the signer certificate, and the
        # signer's public key.
        "freetsa": AnchorSpec(
            filename="freetsa-root-2016.pem",
            pem_sha256=(
                "2151b61137ffa86bf664691ba67e7da0b19f98c758e3d228d5d8ebf27e044438"
            ),
            policy_oid="1.2.3.4.1",
            signer_certificate_sha256=(
                "32e841a95cc1164101ffde41298ef2fc75c1c4372ef095e88a6bbd47dfb191fc"
            ),
            signer_spki_sha256=(
                "fa02bd555e3e483d62b4e70be6218692068d2b0b0a7525db58dcbf2901cdb072"
            ),
        ),
        "digicert": AnchorSpec(
            filename="digicert-trusted-root-g4.pem",
            pem_sha256=(
                "ce7d6b44f5d510391be98c8d76b18709400a30cd87659bfebe1c6f97ff5181ee"
            ),
            policy_oid="2.16.840.1.114412.7.1",
            signer_certificate_sha256=(
                "4aa03fa22cd75c84c55c938f828e676b9caecab33fe36d269aa334f146110a33"
            ),
            signer_spki_sha256=(
                "7abda95ed7301ac94bded350babc319903d0b4f16c4e7e39346dba5f9e992b72"
            ),
        ),
    },
)

CORPUS = CorpusSpec(
    schema_version=JOURNAL_SCHEMA,
    # Everything under nz/ with a .yaml suffix is swept closed-world: the
    # journal must bind exactly the files present, no more and no fewer.
    content_roots=(pathlib.PurePosixPath("nz"),),
    content_suffixes=(".yaml",),
    required_attested_paths=ATTESTED_PATHS,
    # This lane has no gate that depends on licensed or otherwise restricted
    # inputs, so "restricted" is deliberately NOT accepted: introducing one
    # must be a reviewed change to this file, not a quiet new row in a journal.
    accepted_gate_tiers=frozenset({"public", "ci-attested"}),
    # Gates the journal MUST declare. `guard/manual-rulespec-changes` is
    # required precisely because it does not currently run: requiring it forces
    # the journal to say so out loud instead of omitting it, which would read
    # identically to a gate that passed.
    required_gates=frozenset(
        {
            "rulespec/validate-yaml",
            "rulespec/companion-tests",
            "rulespec/proofs-and-claims",
            "repo/layout",
            "waivers/ratchet-audit",
            "guard/manual-rulespec-changes",
        }
    ),
)

SPEC = VerificationSpec(
    name="rulespec-nz published corpus",
    chain=CHAIN,
    corpus=CORPUS,
)

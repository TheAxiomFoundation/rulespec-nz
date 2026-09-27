# Verify this corpus yourself

Everything else in this repository is a claim we make about our own work. This
page is the one that does not depend on trusting us.

```bash
git clone https://github.com/TheAxiomFoundation/rulespec-nz
cd rulespec-nz
uv tool install "receipt>=0.5"
receipt verify --spec verification/spec.py
```

The clone and the install need the network; verification itself does not, and
you can disconnect before running it. This corpus was cut against `receipt`
0.5.0 — a later release may verify *more* strictly, never less, since every
pass is fail-closed. To reproduce exactly what we ran, pin `receipt==0.5.0`.

No account, no API key, no cooperation from us. `openssl` and Python are the
only tools involved. The command exits `0` if the corpus is exactly what it
says it is and `1` otherwise (`2` for usage errors — a missing spec or a bad
path), and it prints why either way.

## What a passing verdict establishes

Every `.yaml` file under `nz/` is listed by SHA-256 in an append-only journal.
That journal is covered by a release manifest, the manifest is signed by an
Ed25519 key, and the manifest's digest is timestamped by two independent RFC
3161 authorities. A pass means all of the following held:

- **The rule files are the exact bytes that were signed and witnessed.** One
  changed character in one `nz/**.yaml` file fails the verdict.
- **The file set is closed.** A rule file added to the tree without being
  witnessed fails. A witnessed file deleted from the tree fails. There is no
  "extra file we forgot to mention."
- **The signing key is the one this repository committed to.** Verification
  pins the SHA-256 of the key's `SubjectPublicKeyInfo` in
  [`verification/spec.py`](verification/spec.py). Swapping the key file in
  `verification/releases/anchors/` changes nothing, because the fingerprint the
  verifier compares against lives in the source tree you just cloned, not
  beside the key.
- **Two unrelated authorities witnessed it.** The timestamp tokens are checked
  against root certificates whose bytes, policy OIDs, signer certificates, and
  signer public keys are each pinned separately in the same file. One
  authority alone cannot move a release's time.
- **The history was not rewritten.** Each release seals the previous journal
  rows byte for byte. A corrected encoding appends a new row; it cannot quietly
  replace an old one.
- **The context is bound too.** The corpus release the encodings resolve
  against (`.axiom/toolchain.toml`), the layout contract, the pinned CI
  workflow, and both known-gap ratchets are all covered by the same signature
  and the same witnesses.

## What it does not establish

**It does not prove the encodings are a correct reading of New Zealand law.**
No cryptography can. It proves that what you are reading is what was published,
unchanged.

**It does not prove your clone holds the newest release.** A stale clone whose
chain was honestly witnessed also passes — the verdict proves custody of what
is present, not freshness. To check you have the latest, compare the release
head against the repository on GitHub (or run with `--base-ref` against a ref
you trust).

**It does not re-run any verification gate.** The journal *declares* which
gates ran, and the command reports those declarations without executing them.
Each declaration carries a reproducibility tier, because "anyone can re-run the
full suite" is not true here and we would rather say so than imply otherwise:

| Tier | Meaning | Count |
|---|---|---|
| `public` | You can re-run it yourself from public inputs. | 11 |
| `ci-attested` | You cannot re-run it as we ran it; only the CI run's identity vouches. | 6 |

The six `ci-attested` gates are honest about why. Five of them —
`rulespec/validate-yaml`, `waivers/ratchet-audit`,
`rulespec/proofs-and-claims`, `rulespec/money-proof-atoms`, and
`guard/manual-rulespec-changes` (which did not run at all; see below) — run
under a protected signing supervisor provisioned with trust roots supplied
from GitHub **organization variables**, which someone outside the organization
cannot read. That is a real limitation and, by the design principle this
repository is adopting, a defect worth naming: those roots belong in committed
code, exactly like the ones in `verification/spec.py`. The sixth,
`schema/retired-freeze`, behaves differently outside a CI event context, so an
offline re-run would not be the same check.

(An earlier draft of this corpus tiered `proofs-and-claims` and
`money-proof-atoms` as `public`; a pre-publication cross-family review caught
the overclaim against the pinned workflow before genesis was cut. The
underlying checks are deterministic over public inputs — it is the supervisor
wrapper that an outsider cannot reproduce.)

### What the declarations are *about*

Every declaration names a `subjectCommit` and states its `subjectScope`, and
neither is this commit. A journal is part of the commit that carries it, so it
cannot cite a CI run of itself — the run necessarily precedes the commit. Read
the declarations as claims about the commit they name:

- For content-determined gates, the subject is the rule content at
  `89a7d25`, which is byte-identical to this release's `nz/` tree. You can
  check that yourself: `git diff 89a7d25 HEAD -- nz/` is empty.
- For the four gates whose result depends on the CI *event* context —
  `repo/tracked-paths`, `waivers/ratchet-audit`, `schema/retired-freeze`, and
  `guard/manual-rulespec-changes` — the outcome is a property of that commit
  and that run. It is recorded as history and explicitly does **not** transfer
  to this tree. Their `subjectScope` says so.

This is the X/X+1 publication problem named in
[axiom-encode#1192](https://github.com/TheAxiomFoundation/axiom-encode/issues/1192)
requirement 5. The notary cutover resolves it properly with detached
attestations; until then the honest move is to state the subject rather than
let "declared" imply "declared about the tree you are holding".

**One declared gate did not run at all.** `guard/manual-rulespec-changes` is
disabled in this repository's workflow (`run-generated-guard: false`), so no
machine check asserts that these rule files carry encoder apply manifests —
`rulespec-nz` has none. The verification spec *requires* that gate to be
declared for exactly this reason: a journal that omitted it would read
identically to one where it passed. Closing that gap is the backfill tracked in
[axiom-encode#1192](https://github.com/TheAxiomFoundation/axiom-encode/issues/1192).

## Check that it actually fails

A verifier that only ever says yes is worth nothing. Break something and watch:

```bash
echo "# tampered" >> nz/statutes/gst/rate.yaml
receipt verify --spec verification/spec.py; echo "exit=$?"
```

```bash
git checkout nz/statutes/gst/rate.yaml
cp nz/statutes/gst/rate.yaml nz/statutes/gst/smuggled.yaml
receipt verify --spec verification/spec.py; echo "exit=$?"
```

Both exit `1`. The first fails on the file's digest, the second on the
closed-world sweep. Restore with `git checkout nz/ && rm -f
nz/statutes/gst/smuggled.yaml`.

You can also confirm the timestamps independently, without `receipt` — using
`openssl ts -verify`, which checks the token's signature against a trust
anchor. (`openssl ts -reply -text` only *decodes* a token; it verifies
nothing, so a token from any signer would print convincingly.)

```bash
MANIFEST=$(ls verification/releases/manifests/*.json)
DIGEST=$(shasum -a 256 "$MANIFEST" | cut -d' ' -f1)
for TSA in freetsa digicert; do
  openssl ts -verify -digest "$DIGEST" \
    -in "${MANIFEST%.json}.$TSA.tsr" \
    -CAfile "verification/releases/anchors/$(ls verification/releases/anchors | grep "^$TSA\|^digicert")" \
    -no_check_time && echo "$TSA: token verifies over the manifest digest"
done
```

Both must print `Verification: OK`. That proves each authority signed *this
manifest's digest*, against the root certificate committed in this repository.
Note what it does not prove: that those root certificates are the authorities'
genuine roots. If you want to close that too, fetch the roots from
[FreeTSA](https://freetsa.org/) and DigiCert yourself and compare against
`verification/releases/anchors/`.

## Reading the trust configuration

[`verification/spec.py`](verification/spec.py) is short, has no logic, and is
the whole trust configuration. Read it. `receipt verify` prints that file's own
SHA-256 with every verdict so you can quote the exact configuration you ran
under, and notice later if it changed.

For machine consumption, `receipt verify --spec verification/spec.py --json`
emits the same verdict as JSON, including a `scope.notEstablished` list that
says in the payload itself what the pass does not cover.

## Scope of this pilot

This is the first corpus wired end to end for third-party verification
(receipt#13). The journal covers this repository's rule files and the context
listed above. It does not yet carry notary-v1 admission receipts — those arrive
with the axiom-encode#1192 cutover and will append to this same chain rather
than replace it.

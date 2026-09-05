"""Build and verify deterministic sanitized derivatives of preserved Stage 5 ZIPs."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import pathlib
import re
import sys
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXED_ZIP_TIME = (2026, 9, 4, 0, 0, 0)
BMAD_TAG_OBJECT = "178414679b11a171ca1597b0ebc1723ed488fc73"
BMAD_COMMIT = "9ce3c397c9b238de96f7365da8019f6f66b059da"

NOTICE_SOURCES = (
    (
        "notices/BMAD-METHOD-v6.11.0/LICENSE",
        "notices/BMAD-METHOD-v6.11.0-LICENSE.txt",
        "https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/LICENSE",
    ),
    (
        "notices/BMAD-METHOD-v6.11.0/CONTRIBUTORS.md",
        "notices/BMAD-METHOD-v6.11.0-CONTRIBUTORS.md",
        "https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/CONTRIBUTORS.md",
    ),
    (
        "notices/BMAD-METHOD-v6.11.0/TRADEMARK.md",
        "notices/BMAD-METHOD-v6.11.0-TRADEMARK.md",
        "https://github.com/bmad-code-org/BMAD-METHOD/blob/v6.11.0/TRADEMARK.md",
    ),
    (
        "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/LICENSE",
        "LICENSE",
        "https://github.com/Isty-org/spec-driven-ai-dev/blob/v1.0.0/LICENSE",
    ),
    (
        "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/NOTICE",
        "notices/ISTY-CLASSIC-NOTICE.txt",
        "https://github.com/Isty-org/spec-driven-ai-dev/blob/v1.0.0/NOTICE",
    ),
    (
        "EVIDENCE-RIGHTS-NOTICE.md",
        "notices/EVIDENCE-RIGHTS-NOTICE.md",
        "https://github.com/Isty-org/agent-workflow-benchmark/blob/v1.0.0/notices/EVIDENCE-RIGHTS-NOTICE.md",
    ),
)

EXPECTED_NOTICE_SHA256 = {
    "notices/BMAD-METHOD-v6.11.0/LICENSE": "0aa79baf6328b4a1e694ce10a12ffc36d7666554da128dff0e8fcda0fc536a66",
    "notices/BMAD-METHOD-v6.11.0/CONTRIBUTORS.md": "1f0d0736ff06fcea2c504834b9d13196f37ca57fae5cf9054899dcec4ed36ad4",
    "notices/BMAD-METHOD-v6.11.0/TRADEMARK.md": "ce57ad749e43277c6021e5d5085980b33c9bf8f67a070bbbf07e041ccdddc58b",
    "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/NOTICE": "2159c5eb9c573e8dbe7d6f11ecdb8d49beea36c1c709bbc1754d765c0ae38049",
}

SECRET_PATTERNS = (
    ("private-key", re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("openai-key", re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("github-token", re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws-access-key", re.compile(rb"\bAKIA[0-9A-Z]{16}\b")),
    ("bearer-token", re.compile(rb"(?i)\bBearer[ \t]+[A-Za-z0-9._~+/-]{24,}={0,2}")),
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def package_name(raw_name: str) -> str:
    if not raw_name.endswith(".zip"):
        raise ValueError(f"Raw asset must be a ZIP: {raw_name}")
    return raw_name[:-4] + "-evidence-package.zip"


def validate_source_path(name: str) -> pathlib.PurePosixPath:
    pure = pathlib.PurePosixPath(name)
    if (
        not name
        or name.endswith("/")
        or pure.is_absolute()
        or ".." in pure.parts
        or "\\" in name
        or (pure.parts and ":" in pure.parts[0])
    ):
        raise ValueError(f"Unsafe source archive path: {name}")
    return pure


def exclusion_reason(name: str) -> str | None:
    pure = validate_source_path(name)
    lowered = tuple(part.lower() for part in pure.parts)
    if len(lowered) >= 2 and lowered[-2:] == ("specs", ".me"):
        return "local identity file prohibited from public packages"
    if "__pycache__" in lowered or lowered[-1].endswith(".pyc"):
        return "generated Python cache artifact prohibited from public packages"
    if len(lowered) >= 2 and lowered[-2:] == (".prist", "connection.json"):
        return "credential-bearing local connection state prohibited from public packages"
    if lowered[-1] in {".ds_store", "thumbs.db"} or lowered[-1].endswith(".tmp"):
        return "local operating-system or scratch artifact prohibited from public packages"
    return None


def zip_info(name: str, mode: int = 0o100644) -> zipfile.ZipInfo:
    validate_source_path(name)
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = mode << 16
    return info


def notice_payloads(root: pathlib.Path = ROOT) -> tuple[dict[str, bytes], list[dict]]:
    payloads: dict[str, bytes] = {}
    records: list[dict] = []
    for package_path, source_path, upstream_url in NOTICE_SOURCES:
        raw = (root / source_path).read_bytes()
        digest = sha256(raw)
        expected_digest = EXPECTED_NOTICE_SHA256.get(package_path)
        if expected_digest is not None and digest != expected_digest:
            raise ValueError(f"Pinned notice identity mismatch: {package_path}")
        payloads[package_path] = raw
        records.append(
            {
                "packagePath": package_path,
                "sourcePath": source_path,
                "sourceUrl": upstream_url,
                "bytes": len(raw),
                "sha256": digest,
            }
        )
    return payloads, records


def classic_scope_payload(root: pathlib.Path = ROOT) -> tuple[bytes, dict, dict[str, dict]]:
    raw = (root / "assets/classic-methodology-scope.json").read_bytes()
    scope = json.loads(raw)
    if scope.get("methodologyCommit") != "b5c3e3c6576570ec348b79305e0d455469d0642c":
        raise ValueError("Classic methodology scope commit mismatch")
    if scope.get("licenseSha256") != EXPECTED_NOTICE_SHA256[
        "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/LICENSE"
    ]:
        raise ValueError("Classic methodology license identity mismatch")
    if scope.get("noticeSha256") != EXPECTED_NOTICE_SHA256[
        "notices/CLASSIC-SPEC-DRIVEN-AI-DEV/NOTICE"
    ]:
        raise ValueError("Classic methodology NOTICE identity mismatch")
    by_path = {item["path"]: item for item in scope["files"]}
    if len(by_path) != 39 or len(by_path) != len(scope["files"]):
        raise ValueError("Classic methodology scope must contain 39 unique files")
    return raw, scope, by_path


def classic_scope_matches(included_records: list[dict], scope_by_path: dict[str, dict]) -> list[dict]:
    matches = []
    for record in included_records:
        parts = record["sourcePath"].split("/", 1)
        if len(parts) != 2 or "-classic-" not in parts[0]:
            continue
        relative = parts[1]
        source = scope_by_path.get(relative)
        if source is None or source["sha256"] != record["sha256"] or source["bytes"] != record["bytes"]:
            continue
        matches.append(
            {
                "packagePath": record["packagePath"],
                "sourcePath": record["sourcePath"],
                "methodologySourcePath": source["sourcePath"],
                "bytes": record["bytes"],
                "sha256": record["sha256"],
                "spdx": "Apache-2.0",
            }
        )
    return sorted(matches, key=lambda item: item["sourcePath"])


@functools.lru_cache(maxsize=None)
def fixture_allowlist(root: pathlib.Path = ROOT) -> set[str]:
    record = read_json(root / "verification/secret-scan.json")
    return {item["sha256"] for item in record.get("fixtureFileHashes", [])}


def secret_findings(source_archive: str, source_path: str, raw: bytes, root: pathlib.Path = ROOT) -> list[str]:
    matches = [name for name, pattern in SECRET_PATTERNS if pattern.search(raw)]
    if not matches:
        return []
    if sha256(raw) in fixture_allowlist(root):
        return []
    return matches


def render_readme(package_filename: str, source: dict, included: int, excluded: int) -> bytes:
    text = f"""# Agent Workflow Benchmark sanitized evidence package

Package: `{package_filename}`

This deterministic public package is a sanitized derivative of the preserved Stage 5 archive `{source['filename']}`. The local source archive remains unchanged at SHA-256 `{source['sha256']}` and size `{source['bytes']}` bytes. This package contains {included} source members with byte-for-byte content identity and excludes {excluded} source members under the public-content policy.

This package is intentionally described as a sanitized derivative. It is not an exact or complete copy of the source archive.

## Verify and inspect

1. Extract this package with any ZIP reader.
2. Verify every extracted member against `SHA256SUMS`.
3. Read `MANIFEST.json` for source-archive provenance, included member hashes, excluded member paths/hashes/sizes, earlier credential hash-only exclusions, and notice sources.
4. Compare `SOURCE-MEMBER-MANIFEST.json` with the committed source inventory when auditing provenance.
5. Inspect preserved content under `evidence/`.

Every evidence member keeps the exact bytes recorded in the source archive. Package paths add only the `evidence/` prefix.

## Rights and provenance

Read `EVIDENCE-RIGHTS-NOTICE.md` before reusing any content. Applicable BMAD Method 6.11.0 MIT, contributor, and trademark notices are under `notices/BMAD-METHOD-v6.11.0/`. The Isty Apache-2.0 license and NOTICE under `notices/CLASSIC-SPEC-DRIVEN-AI-DEV/` cover package metadata and Isty-owned Classic methodology files. Existing notices inside evidence trees stay attached to their original components.

The BMAD name identifies an experimental condition. This package has no endorsement, approval, certification, or sponsorship from BMad Code, LLC.

Local identities must be recreated from `specs/.me.template` when materializing a rerun. Credential-bearing `.prist/connection.json` files remain hash-only provenance records.
"""
    return text.encode("utf-8")


def read_source_members(
    archive: zipfile.ZipFile,
    raw_asset: dict,
    member_manifest: dict,
    root: pathlib.Path,
) -> tuple[dict[str, tuple[bytes, int]], list[dict], list[dict]]:
    expected = {item["path"]: item for item in member_manifest["files"]}
    names = archive.namelist()
    if len(names) != len(set(names)) or set(names) != set(expected):
        raise ValueError(f"Source member inventory mismatch: {raw_asset['name']}")
    included: dict[str, tuple[bytes, int]] = {}
    included_records: list[dict] = []
    excluded_records: list[dict] = []
    for name in names:
        validate_source_path(name)
        raw = archive.read(name)
        expected_item = expected[name]
        if len(raw) != expected_item["bytes"] or sha256(raw) != expected_item["sha256"]:
            raise ValueError(f"Source member identity mismatch: {raw_asset['name']}:{name}")
        reason = exclusion_reason(name)
        record = {"sourcePath": name, "bytes": len(raw), "sha256": sha256(raw)}
        if reason:
            record["reason"] = reason
            excluded_records.append(record)
            continue
        findings = secret_findings(raw_asset["name"], name, raw, root)
        if findings:
            raise ValueError(
                f"Unresolved secret-like content in {raw_asset['name']}:{name}: {','.join(findings)}"
            )
        package_path = f"evidence/{name}"
        mode = int(str(expected_item.get("mode", "100644")), 8)
        included[package_path] = (raw, mode)
        included_records.append({**record, "packagePath": package_path, "mode": f"{mode:o}"})
    return included, sorted(included_records, key=lambda item: item["sourcePath"]), sorted(
        excluded_records, key=lambda item: item["sourcePath"]
    )


def build_package(
    raw_path: pathlib.Path,
    raw_asset: dict,
    destination: pathlib.Path,
    root: pathlib.Path = ROOT,
    member_manifest: dict | None = None,
) -> dict:
    raw_archive = raw_path.read_bytes()
    if len(raw_archive) != raw_asset["bytes"] or sha256(raw_archive) != raw_asset["sha256"]:
        raise ValueError(f"Raw archive identity mismatch: {raw_asset['name']}")
    if member_manifest is None:
        member_manifest_raw = (root / raw_asset["manifest"]).read_bytes()
        member_manifest = json.loads(member_manifest_raw)
    else:
        member_manifest_raw = (
            json.dumps(member_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8")

    with zipfile.ZipFile(raw_path) as source_zip:
        included, included_records, excluded_records = read_source_members(
            source_zip, raw_asset, member_manifest, root
        )

    filename = package_name(raw_asset["name"])
    package_path = destination / filename
    notice_data, notice_records = notice_payloads(root)
    classic_scope_raw, classic_scope, scope_by_path = classic_scope_payload(root)
    classic_matches = classic_scope_matches(included_records, scope_by_path)
    if not classic_matches:
        raise ValueError(f"No hash-matched Classic methodology files: {raw_asset['name']}")
    payloads: dict[str, tuple[bytes, int]] = dict(included)
    payloads.update({name: (raw, 0o100644) for name, raw in notice_data.items()})
    payloads["SOURCE-MEMBER-MANIFEST.json"] = (member_manifest_raw, 0o100644)
    payloads["CLASSIC-FILE-SCOPE.json"] = (classic_scope_raw, 0o100644)

    source = {
        "filename": raw_asset["name"],
        "sourcePath": raw_asset["path"],
        "memberManifest": raw_asset["manifest"],
        "memberManifestPackagePath": "SOURCE-MEMBER-MANIFEST.json",
        "memberManifestBytes": len(member_manifest_raw),
        "memberManifestSha256": sha256(member_manifest_raw),
        "bytes": raw_asset["bytes"],
        "sha256": raw_asset["sha256"],
        "rawMemberCount": len(member_manifest["files"]),
        "rawUncompressedBytes": sum(item["bytes"] for item in member_manifest["files"]),
        "includedEvidenceMemberCount": len(included_records),
        "excludedRawMemberCount": len(excluded_records),
        "priorHashOnlyExclusions": member_manifest.get("excluded", []),
        "preservation": "local source archive retained byte-for-byte; public package is a sanitized derivative",
    }
    payloads["README.md"] = (
        render_readme(filename, source, len(included_records), len(excluded_records)),
        0o100644,
    )
    manifest = {
        "schemaVersion": 1,
        "packageType": "agent-workflow-benchmark-sanitized-evidence",
        "release": "v1.0.0",
        "packageFilename": filename,
        "sourceArchive": source,
        "sanitization": {
            "contentTransformations": 0,
            "includedMembersRetainSourceBytes": True,
            "excludedMembers": excluded_records,
            "rules": [
                "exclude specs/.me local identity files",
                "exclude __pycache__ and .pyc generated cache artifacts",
                "exclude .prist/connection.json credential state",
                "exclude confirmed operating-system and .tmp scratch artifacts",
                "reject absolute, traversal, backslash, directory, and drive-qualified paths",
            ],
        },
        "upstream": {
            "bmadMethod": {
                "version": "6.11.0",
                "tag": "v6.11.0",
                "tagObject": BMAD_TAG_OBJECT,
                "commit": BMAD_COMMIT,
                "license": "MIT",
                "repository": "https://github.com/bmad-code-org/BMAD-METHOD",
            },
            "classicMethodology": {
                "edition": "classic-2026.08",
                "license": "Apache-2.0",
                "repository": "https://github.com/Isty-org/spec-driven-ai-dev",
            },
        },
        "rights": {
            "notice": "EVIDENCE-RIGHTS-NOTICE.md",
            "purpose": "Public inspection and verification of preserved benchmark evidence",
            "additionalReuseRightsGranted": False,
            "existingTermsPreserved": True,
            "bmadEndorsement": False,
        },
        "classicApacheScope": {
            "definitionPackagePath": "CLASSIC-FILE-SCOPE.json",
            "definitionSha256": sha256(classic_scope_raw),
            "methodologyCommit": classic_scope["methodologyCommit"],
            "license": "Apache-2.0",
            "matchRule": "Classic-run member relative path, raw SHA-256, and byte count all match the scope definition",
            "matchedMemberCount": len(classic_matches),
            "matchedMembers": classic_matches,
        },
        "notices": notice_records,
        "includedEvidenceMembers": included_records,
    }
    manifest_raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )
    payloads["MANIFEST.json"] = (manifest_raw, 0o100644)
    sums_raw = "".join(
        f"{sha256(value)}  {name}\n" for name, (value, _mode) in sorted(payloads.items())
    ).encode("utf-8")
    payloads["SHA256SUMS"] = (sums_raw, 0o100644)

    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as output:
        for name, (value, mode) in sorted(payloads.items()):
            output.writestr(zip_info(name, mode), value)

    package_raw = package_path.read_bytes()
    relative = package_path.relative_to(root).as_posix() if package_path.is_relative_to(root) else str(package_path)
    return {
        "name": filename,
        "sourcePath": relative,
        "mediaType": "application/zip",
        "bytes": len(package_raw),
        "sha256": sha256(package_raw),
        "sourceArchive": source,
        "sanitization": {
            "includedEvidenceMemberCount": len(included_records),
            "excludedRawMemberCount": len(excluded_records),
            "priorHashOnlyExclusionCount": len(source["priorHashOnlyExclusions"]),
        },
        "status": "candidate_verified_locally",
    }


def parse_sums(raw: bytes) -> dict[str, str]:
    result = {}
    for line in raw.decode("utf-8").splitlines():
        digest, name = line.split("  ", 1)
        if name in result:
            raise ValueError(f"Duplicate checksum path: {name}")
        result[name] = digest
    return result


def required_notice_paths() -> set[str]:
    return {item[0] for item in NOTICE_SOURCES}


def inspect_package(
    path: pathlib.Path,
    expected: dict,
    raw_path: pathlib.Path | None = None,
    root: pathlib.Path = ROOT,
) -> dict:
    outer = path.read_bytes()
    if len(outer) != expected["bytes"] or sha256(outer) != expected["sha256"]:
        raise ValueError(f"Package identity mismatch: {expected['name']}")
    with zipfile.ZipFile(path) as package:
        names = package.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate package member: {expected['name']}")
        for name in names:
            pure = validate_source_path(name)
            if exclusion_reason(name):
                raise ValueError(f"Prohibited public member: {expected['name']}:{name}")
            if pure.suffix.lower() == ".zip":
                raise ValueError(f"Nested ZIP prohibited in public package: {expected['name']}:{name}")
        required = required_notice_paths()
        if not required.issubset(names):
            raise ValueError(f"Required notices missing: {expected['name']}")
        if {
            "MANIFEST.json",
            "SHA256SUMS",
            "README.md",
            "SOURCE-MEMBER-MANIFEST.json",
            "CLASSIC-FILE-SCOPE.json",
        } - set(names):
            raise ValueError(f"Package metadata missing: {expected['name']}")
        manifest = json.loads(package.read("MANIFEST.json"))
        source = manifest["sourceArchive"]
        sums = parse_sums(package.read("SHA256SUMS"))
        if set(sums) != set(names) - {"SHA256SUMS"}:
            raise ValueError(f"Checksum coverage mismatch: {expected['name']}")
        for name, digest in sums.items():
            if sha256(package.read(name)) != digest:
                raise ValueError(f"Package member hash mismatch: {expected['name']}:{name}")
        if manifest["rights"]["additionalReuseRightsGranted"] is not False:
            raise ValueError(f"Evidence rights scope widened: {expected['name']}")
        if manifest["rights"]["bmadEndorsement"] is not False:
            raise ValueError(f"BMAD endorsement claim present: {expected['name']}")
        for key in [
            "filename",
            "sourcePath",
            "memberManifest",
            "memberManifestSha256",
            "bytes",
            "sha256",
            "rawMemberCount",
        ]:
            if source.get(key) != expected["sourceArchive"].get(key):
                raise ValueError(f"Source archive provenance mismatch: {expected['name']}:{key}")
        if sha256(package.read("SOURCE-MEMBER-MANIFEST.json")) != source["memberManifestSha256"]:
            raise ValueError(f"Source member manifest mismatch: {expected['name']}")
        classic_scope = manifest["classicApacheScope"]
        if sha256(package.read("CLASSIC-FILE-SCOPE.json")) != classic_scope["definitionSha256"]:
            raise ValueError(f"Classic methodology scope identity mismatch: {expected['name']}")
        if len(classic_scope["matchedMembers"]) != classic_scope["matchedMemberCount"]:
            raise ValueError(f"Classic methodology scope count mismatch: {expected['name']}")
        for item in classic_scope["matchedMembers"]:
            data = package.read(item["packagePath"])
            if item["spdx"] != "Apache-2.0" or len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                raise ValueError(f"Classic methodology scope match failed: {expected['name']}:{item['sourcePath']}")
        notice_by_path = {item["packagePath"]: item for item in manifest["notices"]}
        if set(notice_by_path) != required:
            raise ValueError(f"Notice manifest mismatch: {expected['name']}")
        for notice_path in required:
            data = package.read(notice_path)
            record = notice_by_path[notice_path]
            if len(data) != record["bytes"] or sha256(data) != record["sha256"]:
                raise ValueError(f"Notice identity mismatch: {expected['name']}:{notice_path}")
            pinned = EXPECTED_NOTICE_SHA256.get(notice_path)
            if pinned is not None and record["sha256"] != pinned:
                raise ValueError(f"Pinned notice mismatch: {expected['name']}:{notice_path}")
        included = manifest["includedEvidenceMembers"]
        excluded = manifest["sanitization"]["excludedMembers"]
        if len(included) != source["includedEvidenceMemberCount"]:
            raise ValueError(f"Included member count mismatch: {expected['name']}")
        if len(excluded) != source["excludedRawMemberCount"]:
            raise ValueError(f"Excluded member count mismatch: {expected['name']}")
        package_evidence = {name.removeprefix("evidence/") for name in names if name.startswith("evidence/")}
        included_source = {item["sourcePath"] for item in included}
        excluded_source = {item["sourcePath"] for item in excluded}
        if package_evidence != included_source or included_source & excluded_source:
            raise ValueError(f"Sanitized inventory mismatch: {expected['name']}")
        if len(included_source | excluded_source) != source["rawMemberCount"]:
            raise ValueError(f"Source member accounting mismatch: {expected['name']}")
        for item in included:
            data = package.read(item["packagePath"])
            if len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                raise ValueError(f"Included evidence identity mismatch: {expected['name']}:{item['sourcePath']}")
            findings = secret_findings(source["filename"], item["sourcePath"], data, root)
            if findings:
                raise ValueError(f"Secret-like content in public package: {expected['name']}:{item['sourcePath']}")
        if raw_path is not None:
            raw_archive = raw_path.read_bytes()
            if len(raw_archive) != source["bytes"] or sha256(raw_archive) != source["sha256"]:
                raise ValueError(f"Raw source identity mismatch: {expected['name']}")
            with zipfile.ZipFile(raw_path) as raw_zip:
                if set(raw_zip.namelist()) != included_source | excluded_source:
                    raise ValueError(f"Raw source coverage mismatch: {expected['name']}")
                for item in included:
                    if raw_zip.read(item["sourcePath"]) != package.read(item["packagePath"]):
                        raise ValueError(
                            f"Included member differs from raw source: {expected['name']}:{item['sourcePath']}"
                        )
                for item in excluded:
                    data = raw_zip.read(item["sourcePath"])
                    if len(data) != item["bytes"] or sha256(data) != item["sha256"]:
                        raise ValueError(
                            f"Excluded member provenance mismatch: {expected['name']}:{item['sourcePath']}"
                        )
    return {
        "name": expected["name"],
        "packageBytes": len(outer),
        "packageSha256": sha256(outer),
        "sourceArchiveBytes": source["bytes"],
        "sourceArchiveSha256": source["sha256"],
        "includedEvidenceMembers": len(included),
        "excludedRawMembers": len(excluded),
        "priorCredentialHashesOnly": len(source["priorHashOnlyExclusions"]),
        "noticesVerified": len(required),
        "secretScan": "pass",
    }


def build_all(raw_dir: pathlib.Path, output_dir: pathlib.Path) -> list[dict]:
    source = read_json(ROOT / "assets/release-assets.json")
    return [build_package(raw_dir / asset["name"], asset, output_dir) for asset in source["assets"]]


def verify_all(package_dir: pathlib.Path, raw_dir: pathlib.Path | None) -> list[dict]:
    upload = read_json(ROOT / "assets/release-upload-manifest.json")
    if upload.get("status") != "approved_for_publication":
        raise ValueError("Upload manifest is not approved for publication")
    records = upload["uploads"]
    if len(records) != 9 or any(record.get("status") != "publishable" for record in records):
        raise ValueError("Expected nine publishable sanitized packages")
    return [
        inspect_package(
            package_dir / record["name"],
            record,
            None if raw_dir is None else raw_dir / record["sourceArchive"]["filename"],
        )
        for record in records
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--raw-dir", type=pathlib.Path, default=ROOT / "release-assets")
    build.add_argument("--output", type=pathlib.Path, default=ROOT / "release-assets" / "packages")
    verify = sub.add_parser("verify")
    verify.add_argument("--packages", type=pathlib.Path, default=ROOT / "release-assets" / "packages")
    verify.add_argument("--raw-dir", type=pathlib.Path, default=ROOT / "release-assets")
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = {"status": "pass", "packages": build_all(args.raw_dir.resolve(), args.output.resolve())}
        else:
            result = {
                "status": "pass",
                "packages": verify_all(args.packages.resolve(), args.raw_dir.resolve()),
            }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (KeyError, OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

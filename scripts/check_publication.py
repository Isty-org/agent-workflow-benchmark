"""Validate the public repository layer without requiring release archives."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]

EXPECTED = {
    ("new-project", "Plain"): (69, "0.42385148", 2013443, "33.6"),
    ("new-project", "BMAD"): (69, "1.36481868", 3629356, "60.5"),
    ("new-project", "Classic"): (45, "3.12769884", 4074624, "67.9"),
    ("new-project", "Prist"): (87, "0.26662576", 1257000, "20.9"),
    ("small-project", "Plain"): (35, "10.077087", 4204885, "70.1"),
    ("small-project", "BMAD"): (29, "1.44226984", 3648434, "60.8"),
    ("small-project", "Classic"): (39, "7.90102716", 4194725, "69.9"),
    ("small-project", "Prist"): (69, "0.43872212", 1556000, "25.9"),
    ("large-project", "Plain"): (98, "4.05826076", 3811712, "63.5"),
    ("large-project", "BMAD"): (25, "0.8408026", 2041483, "34.0"),
    ("large-project", "Classic"): (82, "6.09135428", 2394283, "39.9"),
    ("large-project", "Prist"): (98, "0.2068444", 815000, "13.6"),
}

SCENARIOS = {
    "New project": "new-project",
    "Small existing project": "small-project",
    "Large existing project": "large-project",
    "Новый проект": "new-project",
    "Небольшой существующий проект": "small-project",
    "Большой существующий проект": "large-project",
}

CONDITIONS = {
    "Plain": "plain",
    "BMAD": "bmad",
    "Classic": "classic-spec",
    "Prist": "prist",
}


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def extract_results(path: str, errors: list[str]):
    text = (ROOT / path).read_text(encoding="utf-8")
    found = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] not in SCENARIOS or cells[1] not in CONDITIONS:
            continue
        match = re.fullmatch(r"([\d,]+) ms \(([\d.]+) min\)", cells[4])
        if match is None:
            fail(errors, f"Invalid elapsed cell in {path}: {line}")
            continue
        key = (SCENARIOS[cells[0]], cells[1])
        value = (
            int(cells[2]),
            cells[3].removeprefix("$"),
            int(match.group(1).replace(",", "")),
            match.group(2),
        )
        if key in found:
            fail(errors, f"Duplicate result row in {path}: {key}")
        found[key] = value
    if found != EXPECTED:
        missing = sorted(set(EXPECTED) - set(found))
        extra = sorted(set(found) - set(EXPECTED))
        changed = sorted(key for key in set(found) & set(EXPECTED) if found[key] != EXPECTED[key])
        fail(errors, f"README result mismatch in {path}: missing={missing}, extra={extra}, changed={changed}")
    return text, found


def verify_source_snapshot(errors: list[str]) -> None:
    source = read_json("reports/benchmark-v7-final/source-snapshot.json")
    aggregates = source["aggregate"]
    for (scenario, method), (quality, cost, elapsed, _minutes) in EXPECTED.items():
        row = aggregates[f"{scenario}/{CONDITIONS[method]}"]
        if row["quality"]["median"] != quality:
            fail(errors, f"Quality source mismatch: {scenario}/{method}")
        if str(row["taskCostUsd"]["median"]) != cost:
            fail(errors, f"Cost source mismatch: {scenario}/{method}")
        if row["taskElapsedMs"]["median"] != elapsed:
            fail(errors, f"Elapsed source mismatch: {scenario}/{method}")


def verify_payload_lock(errors: list[str]) -> None:
    lock = read_json("verification/stage5-payload-lock.json")
    for expected in lock["scope"]:
        directory = ROOT / expected["directory"]
        files = sorted(path for path in directory.rglob("*") if path.is_file())
        lines = []
        total_bytes = 0
        for path in files:
            raw = path.read_bytes()
            total_bytes += len(raw)
            relative = path.relative_to(ROOT).as_posix()
            lines.append(f"{hashlib.sha256(raw).hexdigest()} {len(raw)} {relative}\n")
        digest = hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()
        actual = {"files": len(files), "bytes": total_bytes, "manifestSha256": digest}
        for key, value in actual.items():
            if value != expected[key]:
                fail(errors, f"Stage 5 payload changed in {expected['directory']}: {key}={value}")


def verify_upload_manifest(errors: list[str]) -> None:
    source = read_json("assets/release-assets.json")
    upload = read_json("assets/release-upload-manifest.json")
    source_by_name = {asset["name"]: asset for asset in source["assets"]}
    upload_by_raw = {asset["sourceArchive"]["filename"]: asset for asset in upload["uploads"]}
    if len(source_by_name) != 9 or set(source_by_name) != set(upload_by_raw):
        fail(errors, "Release upload manifest must map nine raw archives to nine sanitized packages")
        return
    if upload.get("status") != "approved_for_publication":
        fail(errors, "Release upload manifest is not approved")
    if upload.get("rawArchivePolicy", {}).get("status") != "preserved_local_not_uploaded":
        fail(errors, "Raw archive no-upload policy is missing")
    for name, source_asset in source_by_name.items():
        candidate = upload_by_raw[name]
        raw = candidate["sourceArchive"]
        comparisons = {
            "sourcePath": source_asset["path"],
            "bytes": source_asset["bytes"],
            "sha256": source_asset["sha256"],
            "memberManifest": source_asset["manifest"],
        }
        for key, value in comparisons.items():
            if raw.get(key) != value:
                fail(errors, f"Raw provenance mismatch: {name}/{key}")
        expected_package = name.removesuffix(".zip") + "-evidence-package.zip"
        if candidate.get("name") != expected_package:
            fail(errors, f"Sanitized package name mismatch: {name}")
        if candidate.get("sourcePath") != f"release-assets/packages/{expected_package}":
            fail(errors, f"Sanitized package path mismatch: {name}")
        if candidate.get("status") != "publishable":
            fail(errors, f"Sanitized package is not publishable: {name}")
        if not re.fullmatch(r"[0-9a-f]{64}", candidate.get("sha256", "")):
            fail(errors, f"Sanitized package checksum missing: {name}")
        sanitization = candidate.get("sanitization", {})
        if sanitization.get("includedEvidenceMemberCount", 0) + sanitization.get(
            "excludedRawMemberCount", 0
        ) != raw.get("rawMemberCount"):
            fail(errors, f"Sanitized package member accounting mismatch: {name}")

    sums = (ROOT / "assets/PACKAGE-SHA256SUMS").read_text(encoding="utf-8").splitlines()
    expected_sums = [f"{item['sha256']}  {item['name']}" for item in upload["uploads"]]
    if sums != expected_sums:
        fail(errors, "PACKAGE-SHA256SUMS differs from upload manifest")

    scope = read_json("assets/classic-methodology-scope.json")
    if scope.get("methodologyCommit") != "b5c3e3c6576570ec348b79305e0d455469d0642c":
        fail(errors, "Classic methodology scope commit mismatch")
    if len(scope.get("files", [])) != 39 or len({item["path"] for item in scope["files"]}) != 39:
        fail(errors, "Classic methodology scope must identify 39 unique files")


def public_files():
    files = [path for path in ROOT.glob("*.md") if path.is_file()]
    files.extend(path for path in (ROOT / ".github").rglob("*") if path.is_file())
    files.extend(path for path in (ROOT / "notices").rglob("*") if path.is_file())
    files.extend(
        path
        for path in (ROOT / "tests").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    files.extend(
        [
            ROOT / "assets/release-upload-manifest.json",
            ROOT / "assets/PACKAGE-SHA256SUMS",
            ROOT / "assets/classic-methodology-scope.json",
            ROOT / "package.json",
            ROOT / "LICENSE",
            ROOT / "scripts/build_evidence_packages.py",
            ROOT / "scripts/index_classic_scope.py",
        ]
    )
    return sorted(set(files))


def scan_public_files(errors: list[str]) -> None:
    local_patterns = [
        re.compile(r"(?i)[a-z]:[\\/]users[\\/]"),
        re.compile(r"/(?:users|home)/", re.IGNORECASE),
        re.compile(r"(?i)agent-benchmark-polygon|prist-benchmark-control"),
    ]
    secret_patterns = [
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ]
    for path in public_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for pattern in local_patterns:
            if pattern.search(text):
                fail(errors, f"Machine-specific path in public file: {relative}")
        for pattern in secret_patterns:
            if pattern.search(text):
                fail(errors, f"Secret-like value in public file: {relative}")


def verify_required_public_facts(en: str, ru: str, errors: list[str]) -> None:
    if "[Русская версия](README.ru.md)" not in "\n".join(en.splitlines()[:8]):
        fail(errors, "English README lacks a prominent Russian link")
    if "[English version](README.md)" not in "\n".join(ru.splitlines()[:8]):
        fail(errors, "Russian README lacks a prominent English link")
    shared = [
        "classic-2026.08",
        "gpt-5.6-luna",
        "xhigh",
        "29,710,054",
        "$1.14781888",
        "v7-new-bmad-r3",
        "v7-new-plain-r2",
        "Verify",
        "Re-evaluate",
        "Rerun",
    ]
    for value in shared:
        if value not in en or value not in ru:
            fail(errors, f"Bilingual README fact missing: {value}")
    if "27 V7 Plain/BMAD/Classic tasks" not in en or "9 permissions-corrected V7C Prist tasks" not in en:
        fail(errors, "English README lacks exact 27 V7 + 9 V7C provenance")
    if "27 задач V7 для Plain/BMAD/Classic" not in ru or "9 permissions-corrected задач V7C для Prist" not in ru:
        fail(errors, "Russian README lacks exact 27 V7 + 9 V7C provenance")
    if "total lifecycle cost" not in en.lower() or "total lifecycle cost" not in ru.lower():
        fail(errors, "Measured-task cost boundary is incomplete")


def verify_license(errors: list[str]) -> None:
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Apache License" not in license_text or "Version 2.0, January 2004" not in license_text:
        fail(errors, "LICENSE is not Apache-2.0 text")
    notes = (ROOT / "LICENSE-NOTES.md").read_text(encoding="utf-8")
    third_party = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for value in ["data/", "protocol/", "evidence/", "release-assets/", "BMAD", "Classic", "Prist"]:
        if value not in notes:
            fail(errors, f"License scope omission: {value}")
    for value in [
        "BMAD Method 6.11.0",
        "classic-2026.08",
        "v6.11.0",
        "MIT",
        "TRADEMARK",
        "sanitized",
        "no additional",
    ]:
        if value not in third_party:
            fail(errors, f"Third-party notice omission: {value}")


def main() -> int:
    errors: list[str] = []
    en, en_rows = extract_results("README.md", errors)
    ru, ru_rows = extract_results("README.ru.md", errors)
    if en_rows != ru_rows:
        fail(errors, "English and Russian result tables differ")
    verify_source_snapshot(errors)
    verify_payload_lock(errors)
    verify_upload_manifest(errors)
    verify_required_public_facts(en, ru, errors)
    verify_license(errors)
    scan_public_files(errors)
    result = {
        "status": "pass" if not errors else "fail",
        "readmeResultRowsVerified": len(en_rows),
        "readmeParity": en_rows == ru_rows == EXPECTED,
        "stage5PayloadDirectoriesVerified": 3,
        "releaseAssetsInUploadManifest": 9,
        "publicFilesScanned": len(public_files()),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

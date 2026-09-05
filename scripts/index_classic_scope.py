"""Create the hash-defined Apache-2.0 scope for the frozen Classic methodology."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess


DEFAULT_COMMIT = "b5c3e3c6576570ec348b79305e0d455469d0642c"
PREFIX = "methodology/ru/"


def git(repo: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True
    ).stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--methodology-repo", type=pathlib.Path, required=True)
    parser.add_argument("--commit", default=DEFAULT_COMMIT)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[1]
        / "assets/classic-methodology-scope.json",
    )
    args = parser.parse_args()
    repo = args.methodology_repo.resolve()
    resolved = git(repo, "rev-parse", f"{args.commit}^{{commit}}").decode().strip()
    if resolved != args.commit:
        raise ValueError(f"Unexpected methodology commit: {resolved}")
    records = []
    for item in git(repo, "ls-tree", "-r", "-z", args.commit, PREFIX).split(b"\0"):
        if not item:
            continue
        metadata, encoded_path = item.split(b"\t", 1)
        mode, kind, blob = metadata.decode().split()
        path = encoded_path.decode()
        if kind != "blob" or not path.startswith(PREFIX):
            raise ValueError(f"Unexpected methodology tree entry: {path}")
        raw = git(repo, "show", f"{args.commit}:{path}")
        records.append(
            {
                "path": path.removeprefix(PREFIX),
                "sourcePath": path,
                "mode": mode,
                "gitBlob": blob,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    output = {
        "schemaVersion": 1,
        "edition": "classic-2026.08",
        "language": "ru",
        "methodologyRepository": "https://github.com/Isty-org/spec-driven-ai-dev",
        "methodologyCommit": args.commit,
        "license": "Apache-2.0",
        "licenseSha256": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
        "noticeSha256": "2159c5eb9c573e8dbe7d6f11ecdb8d49beea36c1c709bbc1754d765c0ae38049",
        "scopeRule": "Only package members whose relative path and raw SHA-256 match this inventory are covered as Isty-owned Classic methodology files.",
        "files": sorted(records, key=lambda record: record["path"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"files": len(records), "commit": args.commit, "output": str(args.output)}))


if __name__ == "__main__":
    main()

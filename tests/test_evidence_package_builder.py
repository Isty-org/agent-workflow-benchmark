import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_evidence_packages", ROOT / "scripts/build_evidence_packages.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

PUBLICATION_SPEC = importlib.util.spec_from_file_location(
    "check_publication", ROOT / "scripts/check_publication.py"
)
PUBLICATION_MODULE = importlib.util.module_from_spec(PUBLICATION_SPEC)
assert PUBLICATION_SPEC.loader is not None
PUBLICATION_SPEC.loader.exec_module(PUBLICATION_MODULE)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class EvidencePackageBuilderTests(unittest.TestCase):
    def make_fixture(self, base):
        classic = b"specs/.me\n.human/shortcuts.md\n"
        members = {
            "v7-new-classic-r1/.gitignore": classic,
            "v7-new-classic-r1/specs/.me": b"handle: @local\n",
            "v7-new-bmad-r1/__pycache__/serve.cpython-312.pyc": b"compiled-cache",
            "v7-new-plain-r1/app.txt": b"public evidence\n",
        }
        raw_path = base / "fixture.zip"
        with zipfile.ZipFile(raw_path, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, raw in members.items():
                archive.writestr(name, raw)
        raw_archive = raw_path.read_bytes()
        manifest = {
            "files": [
                {"path": name, "bytes": len(raw), "sha256": digest(raw), "mode": "100644"}
                for name, raw in members.items()
            ],
            "excluded": [
                {
                    "runId": "v7c-new-prist-r1",
                    "path": ".prist/connection.json",
                    "sha256": "1" * 64,
                    "reason": "credential/local connection state; hash only",
                }
            ],
        }
        asset = {
            "name": "fixture.zip",
            "path": "release-assets/fixture.zip",
            "bytes": len(raw_archive),
            "sha256": digest(raw_archive),
            "manifest": "assets/manifests/fixture.json",
        }
        return raw_path, asset, manifest

    def build_fixture(self, base):
        raw_path, asset, manifest = self.make_fixture(base)
        first = MODULE.build_package(raw_path, asset, base / "first", ROOT, manifest)
        second = MODULE.build_package(raw_path, asset, base / "second", ROOT, manifest)
        first_path = base / "first" / first["name"]
        second_path = base / "second" / second["name"]
        self.assertEqual(first_path.read_bytes(), second_path.read_bytes())
        return raw_path, first_path, first

    def rewrite(self, source, destination, mutate):
        with zipfile.ZipFile(source) as archive:
            payloads = {name: archive.read(name) for name in archive.namelist()}
        mutate(payloads)
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, raw in sorted(payloads.items()):
                archive.writestr(MODULE.zip_info(name), raw)

    def tampered_expected(self, record, path):
        result = copy.deepcopy(record)
        raw = path.read_bytes()
        result["bytes"] = len(raw)
        result["sha256"] = digest(raw)
        return result

    def test_build_is_deterministic_and_sanitizes_without_transforming_included_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            result = MODULE.inspect_package(package_path, record, raw_path, ROOT)
            self.assertEqual(result["includedEvidenceMembers"], 2)
            self.assertEqual(result["excludedRawMembers"], 2)
            self.assertEqual(result["priorCredentialHashesOnly"], 1)
            with zipfile.ZipFile(package_path) as archive:
                names = archive.namelist()
                self.assertNotIn("evidence/v7-new-classic-r1/specs/.me", names)
                self.assertFalse(any(name.endswith(".pyc") for name in names))
                self.assertNotIn("evidence/fixture.zip", names)
                self.assertEqual(
                    archive.read("evidence/v7-new-plain-r1/app.txt"), b"public evidence\n"
                )

    def test_public_package_rejects_me_member(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "me.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.__setitem__("evidence/run/specs/.me", b"identity"),
            )
            with self.assertRaisesRegex(ValueError, "Prohibited public member"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)

    def test_public_package_rejects_pyc_member(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "pyc.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.__setitem__("evidence/run/__pycache__/app.pyc", b"cache"),
            )
            with self.assertRaisesRegex(ValueError, "Prohibited public member"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)

    def test_public_package_rejects_nested_zip_member(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "nested.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.__setitem__("attachments/unrelated.zip", b"nested archive"),
            )
            with self.assertRaisesRegex(ValueError, "Nested ZIP prohibited"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)

    def test_source_archive_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path = base / "unsafe.zip"
            with zipfile.ZipFile(raw_path, "w") as archive:
                archive.writestr("../escape.txt", b"escape")
            raw = raw_path.read_bytes()
            asset = {
                "name": "unsafe.zip",
                "path": "release-assets/unsafe.zip",
                "bytes": len(raw),
                "sha256": digest(raw),
                "manifest": "assets/manifests/unsafe.json",
            }
            manifest = {
                "files": [
                    {
                        "path": "../escape.txt",
                        "bytes": 6,
                        "sha256": digest(b"escape"),
                        "mode": "100644",
                    }
                ],
                "excluded": [],
            }
            with self.assertRaisesRegex(ValueError, "Unsafe source archive path"):
                MODULE.build_package(raw_path, asset, base / "output", ROOT, manifest)

    def test_changed_included_member_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "changed.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.__setitem__("evidence/v7-new-plain-r1/app.txt", b"changed"),
            )
            with self.assertRaisesRegex(ValueError, "Package member hash mismatch"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)

    def test_wrong_raw_provenance_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            expected = copy.deepcopy(record)
            expected["sourceArchive"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "Source archive provenance mismatch"):
                MODULE.inspect_package(package_path, expected, raw_path, ROOT)

    def test_missing_notice_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "missing-notice.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.pop("notices/BMAD-METHOD-v6.11.0/LICENSE"),
            )
            with self.assertRaisesRegex(ValueError, "Required notices missing"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)

    def test_tampered_notice_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            base = pathlib.Path(folder)
            raw_path, package_path, record = self.build_fixture(base)
            tampered = base / "tampered-notice.zip"
            self.rewrite(
                package_path,
                tampered,
                lambda items: items.__setitem__(
                    "notices/BMAD-METHOD-v6.11.0/LICENSE", b"changed license"
                ),
            )
            with self.assertRaisesRegex(ValueError, "Package member hash mismatch"):
                MODULE.inspect_package(tampered, self.tampered_expected(record, tampered), raw_path, ROOT)


class PublicationPortabilityTests(unittest.TestCase):
    def test_stage5_path_order_is_independent_of_host_path_flavor(self):
        paths = [
            "protocol/benchmark/README.md",
            "protocol/benchmark.json",
            "protocol/Benchmark.md",
            "protocol/benchmark/evaluator/checker.md",
        ]
        accepted_windows_order = sorted(paths, key=pathlib.PureWindowsPath)
        native_posix_order = sorted(paths, key=pathlib.PurePosixPath)
        canonical_order = sorted(paths, key=PUBLICATION_MODULE.canonical_relative_path_key)
        self.assertNotEqual(accepted_windows_order, native_posix_order)
        self.assertEqual(accepted_windows_order, canonical_order)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Create and independently verify the source ZIP, Git bundle, prompt, and checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str, cwd: Path = ROOT, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        text=True,
        capture_output=capture,
    )


def _git(*args: str) -> str:
    return _run("git", *args, capture=True).stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version() -> str:
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(payload["project"]["version"])


def _ensure_releaseable(tag: str) -> str:
    status = _git("status", "--porcelain=v1", "--untracked-files=all")
    if status:
        raise SystemExit("Working tree must be clean before packaging:\n" + status)
    commit = _git("rev-parse", "HEAD")
    tagged_commit = _git("rev-list", "-n", "1", tag)
    if tagged_commit != commit:
        raise SystemExit(f"Tag {tag!r} does not point to HEAD {commit}")
    return commit


def _artifact_record(path: Path) -> dict[str, Any]:
    return {
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _verify_zip(path: Path, expected_prefix: str) -> None:
    _run("unzip", "-tq", str(path), cwd=path.parent)
    listing = _run("unzip", "-Z1", str(path), cwd=path.parent, capture=True).stdout.splitlines()
    if not listing or any(not item.startswith(expected_prefix + "/") for item in listing):
        raise SystemExit("ZIP does not contain the expected single top-level prefix")
    prohibited = ("/.git/", "/.venv/", "/data/licensed/", "/data/private/", "/data/raw/")
    if any(any(token in f"/{item}" for token in prohibited) for item in listing):
        raise SystemExit("ZIP contains a prohibited path")


def _verify_bundle(path: Path, commit: str, tag: str) -> None:
    _run("git", "bundle", "verify", str(path), cwd=path.parent)
    with tempfile.TemporaryDirectory(prefix="ctw-bundle-verify-") as temp_dir:
        clone = Path(temp_dir) / "clone"
        _run("git", "clone", "--quiet", str(path), str(clone), cwd=path.parent)
        cloned_commit = _run("git", "rev-parse", "HEAD", cwd=clone, capture=True).stdout.strip()
        if cloned_commit != commit:
            raise SystemExit("Cloned bundle revision differs from packaged revision")
        cloned_tag = _run("git", "rev-list", "-n", "1", tag, cwd=clone, capture=True).stdout.strip()
        if cloned_tag != commit:
            raise SystemExit("Cloned bundle tag differs from packaged revision")


def package(output_dir: Path, *, tag: str | None = None) -> tuple[Path, ...]:
    """Build all handover artefacts and return their paths."""
    version = _version()
    release_tag = tag or f"v{version}-handover"
    commit = _ensure_releaseable(release_tag)
    stem = f"closer-to-whom-v{version}-handover"
    prefix = stem

    output_dir.mkdir(parents=True, exist_ok=True)
    for old in output_dir.glob(f"{stem}*"):
        if old.is_file():
            old.unlink()

    source_zip = output_dir / f"{stem}.zip"
    bundle = output_dir / f"{stem}.bundle"
    prompt = output_dir / f"{stem}-CODEX_INTEGRATION_PROMPT.md"
    validation = output_dir / f"{stem}-VALIDATION.md"
    release_notes = output_dir / f"{stem}-RELEASE_NOTES.md"
    manifest = output_dir / f"{stem}-release-manifest.json"
    checksums = output_dir / f"{stem}-SHA256SUMS"

    _run(
        "git",
        "archive",
        "--format=zip",
        f"--prefix={prefix}/",
        f"--output={source_zip}",
        commit,
    )
    _run("git", "bundle", "create", str(bundle), "--all")
    shutil.copy2(ROOT / "CODEX_INTEGRATION_PROMPT.md", prompt)
    shutil.copy2(ROOT / "VALIDATION.md", validation)
    shutil.copy2(ROOT / "release/BOOTSTRAP_RELEASE_NOTES.md", release_notes)

    _verify_zip(source_zip, prefix)
    _verify_bundle(bundle, commit, release_tag)

    tracked_files = _git("ls-tree", "-r", "--name-only", commit).splitlines()
    artifact_records = [
        _artifact_record(item) for item in (source_zip, bundle, prompt, validation, release_notes)
    ]
    manifest_payload = {
        "schema_version": "1.0.0",
        "project": "closer-to-whom",
        "version": version,
        "tag": release_tag,
        "git_revision": commit,
        "canonical_branch": _git("branch", "--show-current"),
        "tracked_file_count": len(tracked_files),
        "source_archive_prefix": prefix,
        "claim_boundary": (
            "Public-data aggregate policy simulation scaffold and synthetic demonstration only; "
            "not an observed service, capacity, patient-journey, waiting-time, or clinical-outcome estimate."
        ),
        "artifacts": artifact_records,
        "verification": {
            "zip_tested": True,
            "zip_prohibited_paths_absent": True,
            "bundle_verified": True,
            "bundle_cloned": True,
            "clone_revision_matches": True,
            "tag_matches_revision": True,
        },
    }
    manifest.write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    checksum_targets = (source_zip, bundle, prompt, validation, release_notes, manifest)
    checksums.write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in checksum_targets),
        encoding="utf-8",
    )
    _run("sha256sum", "-c", checksums.name, cwd=output_dir)
    return source_zip, bundle, prompt, validation, release_notes, manifest, checksums


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "dist/handover",
        help="Directory into which verified handover artefacts are written.",
    )
    parser.add_argument("--tag", help="Release tag; defaults to v<project-version>-handover.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for artifact in package(args.output_dir.resolve(), tag=args.tag):
        print(artifact)


if __name__ == "__main__":
    main()

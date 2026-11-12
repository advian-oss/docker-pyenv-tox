"""Tests for the Bake generator and manifest merge CLI."""

import json
from pathlib import Path

import pytest

import create_builds


def make_metadata(digest: str) -> dict[str, dict[str, str]]:
    """Build metadata for every Bake target."""
    return {
        create_builds.target_name(target, variant): {"containerimage.digest": f"sha256:{digest * 64}"}
        for target in create_builds.TARGETS
        for variant in create_builds.VARIANTS
    }


def test_all_bakefile_uses_architecture_cache_and_weekly_epoch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Use a separate cache for each architecture."""
    monkeypatch.setenv("BUILD_DATE", "2026-11-11")
    monkeypatch.delenv("CACHE_EPOCH", raising=False)

    create_builds.print_bakefile("advian", "all")

    output = capsys.readouterr().out
    assert 'targets = ["pyenv-alpine-323"' in output
    assert 'targets = ["tox-base-alpine-323"' in output
    assert 'variable "CACHE_EPOCH" { default = "2026-W46" }' in output
    assert "ref=${CACHE_REPO}:debian-trixie-amd64" in output
    assert "ref=${CACHE_REPO}:debian-trixie-arm64" in output
    assert "mode=max,image-manifest=true,oci-mediatypes=true" in output
    assert "tags = PUSH_BY_DIGEST ? []" in output
    assert 'output = BUILD_ARCH != "" && PUSH_BY_DIGEST ?' in output


def test_merge_dry_run_assigns_tags_and_uses_both_digests(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Merge both architecture digests."""
    monkeypatch.setenv("DHUBREPO", "advian")
    monkeypatch.setenv("BUILD_DATE", "2026-11-11")
    metadata_paths = []
    for architecture, digest in zip(create_builds.ARCHITECTURES, ("a", "b")):
        metadata_path = tmp_path / f"meta-{architecture}.json"
        metadata_path.write_text(json.dumps(make_metadata(digest)), encoding="utf-8")
        metadata_paths.append(str(metadata_path))

    result = create_builds.main(["merge", "--dry-run", *metadata_paths])

    output = capsys.readouterr().out
    assert result == 0
    assert len(output.splitlines()) == len(create_builds.TARGETS) * len(create_builds.VARIANTS)
    assert "advian/pyenv:debian-2026-11-11" in output
    assert f"advian/pyenv@sha256:{'a' * 64}" in output
    assert f"advian/pyenv@sha256:{'b' * 64}" in output


def test_merge_fails_if_a_target_is_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """Reject incomplete build metadata."""
    monkeypatch.setenv("DHUBREPO", "advian")
    valid_metadata = tmp_path / "meta-valid.json"
    valid_metadata.write_text(json.dumps(make_metadata("a")), encoding="utf-8")
    missing_metadata = tmp_path / "meta-missing.json"
    missing_metadata.write_text("{}", encoding="utf-8")

    result = create_builds.main(["merge", "--dry-run", str(valid_metadata), str(missing_metadata)])

    assert result == 1
    assert "missing target" in capsys.readouterr().err

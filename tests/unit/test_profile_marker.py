from pathlib import Path

import pytest

from dotaws.project.profile_marker import find_nearest_marker
from dotaws.shared.errors import ProfileResolutionError


def test_find_nearest_marker_uses_nearest_parent(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "root"
    nested = root / "a" / "b"
    nested.mkdir(parents=True)
    (root / ".aws_profile").write_text("root", encoding="utf-8")
    (root / "a" / ".aws_profile").write_text("inner", encoding="utf-8")
    monkeypatch.chdir(nested)

    marker = find_nearest_marker()
    assert marker is not None
    assert marker.profile_name == "inner"


def test_empty_marker_raises(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / ".aws_profile").write_text("\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ProfileResolutionError):
        find_nearest_marker()

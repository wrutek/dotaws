"""Project profile marker resolution."""

from pathlib import Path

from dotaws.shared.errors import ProfileResolutionError
from dotaws.shared.models import ProjectProfileMarker

MARKER_FILE = ".aws_profile"


def find_nearest_marker(start_dir: str | Path | None = None) -> ProjectProfileMarker | None:
    current = Path(start_dir or Path.cwd()).resolve()
    for depth, parent in enumerate([current, *current.parents]):
        marker = parent / MARKER_FILE
        if marker.exists():
            try:
                profile_name = marker.read_text(encoding="utf-8").strip()
            except OSError as exc:
                raise ProfileResolutionError(
                    "Could not read .aws_profile marker.",
                    hint=str(exc),
                ) from exc
            if not profile_name:
                raise ProfileResolutionError(".aws_profile is empty.")
            return ProjectProfileMarker(
                file_path=str(marker),
                directory=str(parent),
                profile_name=profile_name,
                depth_from_cwd=depth,
            )
    return None

from __future__ import annotations

import sys
from typing import TextIO

BAR_WIDTH = 24


def format_duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "--:--"
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def format_bar(done: float, total: float | None, speed: float | None, eta: float | None) -> str:
    speed_text = f"{speed / 1024 / 1024:.1f} MiB/s" if speed else "-- MiB/s"
    if not total:
        return f"[{'.' * BAR_WIDTH}] {done / 1024 / 1024:.1f} MiB  {speed_text}"

    fraction = max(0.0, min(1.0, done / total))
    filled = int(fraction * BAR_WIDTH)
    bar = "#" * filled + "-" * (BAR_WIDTH - filled)
    return f"[{bar}] {fraction:4.0%}  {speed_text}  ETA {format_duration(eta)}"


class ProgressBar:
    """Single-line download bar drawn on stderr. Draws nothing when stderr is not a terminal."""

    def __init__(self, stream: TextIO | None = None) -> None:
        self.stream = stream or sys.stderr
        self.enabled = self.stream.isatty()
        self._drawn = False

    def hook(self, data: dict) -> None:
        if not self.enabled:
            return

        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            line = format_bar(data.get("downloaded_bytes") or 0, total, data.get("speed"), data.get("eta"))
            self.stream.write(f"\r  {line}   ")
            self.stream.flush()
            self._drawn = True
        elif status == "finished":
            self.finish()

    def finish(self) -> None:
        if self._drawn:
            self.stream.write("\n")
            self.stream.flush()
            self._drawn = False

    def note(self, message: str) -> None:
        if self.enabled:
            self.stream.write(f"  {message}\n")
            self.stream.flush()

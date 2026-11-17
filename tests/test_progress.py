import io

from tunefetch.progress import ProgressBar, format_bar, format_duration


class Tty(io.StringIO):
    def isatty(self) -> bool:
        return True


def test_format_duration():
    assert format_duration(65) == "1:05"
    assert format_duration(3725) == "1:02:05"
    assert format_duration(None) == "--:--"


def test_format_bar_with_known_total():
    line = format_bar(50, 100, 2 * 1024 * 1024, 3)
    assert "[############------------]" in line
    assert "50%" in line and "2.0 MiB/s" in line and "ETA 0:03" in line


def test_format_bar_without_total_does_not_divide_by_zero():
    assert "1.0 MiB" in format_bar(1024 * 1024, None, None, None)


def test_progress_bar_draws_only_on_a_terminal():
    quiet = io.StringIO()
    ProgressBar(quiet).hook({"status": "downloading", "downloaded_bytes": 5, "total_bytes": 10})
    assert quiet.getvalue() == ""

    stream = Tty()
    bar = ProgressBar(stream)
    bar.hook({"status": "downloading", "downloaded_bytes": 5, "total_bytes": 10})
    bar.hook({"status": "finished"})
    assert "50%" in stream.getvalue()
    assert stream.getvalue().endswith("\n")

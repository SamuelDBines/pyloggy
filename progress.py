"""Local helper script for trying pyloggy progress/timer APIs quickly."""

from loggy import ProgressTracker, Stopwatch


def demo() -> None:
    with Stopwatch() as sw:
        tracker = ProgressTracker(total=5)
        for _ in range(5):
            tracker.advance()
            print(tracker.render())
    print(f"done in {Stopwatch.format_seconds(sw.elapsed)}")


if __name__ == "__main__":
    demo()

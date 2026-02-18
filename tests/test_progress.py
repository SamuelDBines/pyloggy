import unittest

from loggy import ProgressTracker, Stopwatch, time_call


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, amount: float):
        self.t += amount


class ProgressTests(unittest.TestCase):
    def test_stopwatch_start_stop_and_elapsed(self):
        clock = FakeClock()
        sw = Stopwatch(auto_start=False, clock=clock)

        self.assertFalse(sw.running)
        sw.start()
        self.assertTrue(sw.running)

        clock.advance(1.25)
        self.assertAlmostEqual(sw.elapsed, 1.25)

        sw.stop()
        self.assertFalse(sw.running)
        clock.advance(2.0)
        self.assertAlmostEqual(sw.elapsed, 1.25)

    def test_stopwatch_reset(self):
        clock = FakeClock()
        sw = Stopwatch(auto_start=True, clock=clock)
        clock.advance(0.5)
        sw.reset(auto_start=False)
        self.assertEqual(0.0, sw.elapsed)
        self.assertFalse(sw.running)

    def test_stopwatch_context_manager(self):
        clock = FakeClock()
        with Stopwatch(auto_start=False, clock=clock) as sw:
            clock.advance(0.2)
        self.assertAlmostEqual(sw.elapsed, 0.2)

    def test_format_seconds_variants(self):
        self.assertEqual("250ms", Stopwatch.format_seconds(0.25))
        self.assertEqual("2.50s", Stopwatch.format_seconds(2.5))
        self.assertEqual("1m 5.0s", Stopwatch.format_seconds(65.0))
        self.assertEqual("1h 1m 1.0s", Stopwatch.format_seconds(3661.0))

    def test_lap_matches_elapsed(self):
        clock = FakeClock()
        sw = Stopwatch(auto_start=True, clock=clock)
        clock.advance(0.4)
        self.assertAlmostEqual(sw.elapsed, sw.lap())

    def test_progress_tracker_snapshot_and_render(self):
        clock = FakeClock()
        tracker = ProgressTracker(total=10, clock=clock)
        tracker.advance(4)
        clock.advance(2.0)

        snap = tracker.snapshot()
        self.assertEqual(4, snap.current)
        self.assertEqual(10, snap.total)
        self.assertEqual(6, snap.remaining)
        self.assertAlmostEqual(40.0, snap.percent)
        self.assertAlmostEqual(2.0, snap.elapsed)
        self.assertAlmostEqual(2.0, snap.rate)
        self.assertAlmostEqual(3.0, snap.eta)

        rendered = tracker.render(width=10, fill="=", empty=".")
        self.assertIn("[====......]", rendered)
        self.assertIn("4/10", rendered)

    def test_progress_complete_and_set(self):
        tracker = ProgressTracker(total=3)
        self.assertFalse(tracker.complete)
        tracker.set(3)
        self.assertTrue(tracker.complete)
        self.assertEqual(100.0, tracker.percent)

    def test_progress_constructor_current_bounds(self):
        with self.assertRaises(ValueError):
            ProgressTracker(total=3, current=-1)
        with self.assertRaises(ValueError):
            ProgressTracker(total=3, current=4)

    def test_snapshot_eta_none_until_progress_and_time(self):
        clock = FakeClock()
        tracker = ProgressTracker(total=5, clock=clock)
        snap = tracker.snapshot()
        self.assertIsNone(snap.eta)
        self.assertEqual(0.0, snap.rate)

    def test_render_width_is_clamped_to_one(self):
        clock = FakeClock()
        tracker = ProgressTracker(total=4, current=2, clock=clock)
        out = tracker.render(width=0, fill="=", empty=".")
        self.assertIn("[", out)
        self.assertIn("]", out)
        self.assertIn("2/4", out)

    def test_progress_limits_and_validation(self):
        with self.assertRaises(ValueError):
            ProgressTracker(total=0)

        tracker = ProgressTracker(total=5)
        with self.assertRaises(ValueError):
            tracker.advance(-1)
        with self.assertRaises(ValueError):
            tracker.set(6)

        tracker.advance(99)
        self.assertEqual(5, tracker.current)

    def test_time_call_returns_elapsed_and_result(self):
        clock = FakeClock()

        def work():
            clock.advance(0.75)
            return "ok"

        out = time_call(work, clock=clock)
        self.assertEqual("ok", out["result"])
        self.assertAlmostEqual(0.75, out["elapsed"])

    def test_time_call_propagates_exceptions(self):
        clock = FakeClock()

        def bad():
            clock.advance(0.2)
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            time_call(bad, clock=clock)


if __name__ == "__main__":
    unittest.main()

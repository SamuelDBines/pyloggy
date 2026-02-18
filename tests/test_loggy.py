import io
import os
import unittest

from loggy import Log, LogStyle, STYLES, get_style


class FakeStream(io.StringIO):
    def __init__(self, is_tty: bool):
        super().__init__()
        self._is_tty = is_tty

    def isatty(self):
        return self._is_tty


class LoggyTests(unittest.TestCase):
    def setUp(self):
        self._env_backup = {
            "DEBUG_LOGS": os.environ.get("DEBUG_LOGS"),
            "VERBOSE_LOGS": os.environ.get("VERBOSE_LOGS"),
            "NO_COLOR": os.environ.get("NO_COLOR"),
            "FORCE_COLOR": os.environ.get("FORCE_COLOR"),
        }
        for key in self._env_backup:
            os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self._env_backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def make_logger(self, **kwargs):
        out = kwargs.pop("stream_out", FakeStream(is_tty=False))
        err = kwargs.pop("stream_err", FakeStream(is_tty=False))
        log = Log(stream_out=out, stream_err=err, **kwargs)
        return log, out, err

    def test_ok_warn_go_to_stdout_and_err_goes_to_stderr(self):
        log, out, err = self.make_logger(use_color=False, use_icons=False)

        log.ok("ready")
        log.warn("careful")
        log.err("boom")

        self.assertIn("[OK] ready\n", out.getvalue())
        self.assertIn("[Warn] careful\n", out.getvalue())
        self.assertEqual("[Error] boom\n", err.getvalue())

    def test_log_only_visible_in_debug_mode(self):
        log, out, _ = self.make_logger(use_color=False, use_icons=False, debug=False)
        log.log("hidden")
        self.assertEqual("", out.getvalue())

        log, out, _ = self.make_logger(use_color=False, use_icons=False, debug=True)
        log.log("visible")
        self.assertEqual("[Log] visible\n", out.getvalue())

    def test_info_visible_when_verbose_or_debug(self):
        log, out, _ = self.make_logger(use_color=False, use_icons=False, debug=False, verbose=False)
        log.info("hidden")
        self.assertEqual("", out.getvalue())

        log, out, _ = self.make_logger(use_color=False, use_icons=False, verbose=True)
        log.info("shown")
        self.assertEqual("[Info] shown\n", out.getvalue())

        log, out, _ = self.make_logger(use_color=False, use_icons=False, debug=True)
        log.info("also-shown")
        self.assertEqual("[Info] also-shown\n", out.getvalue())

    def test_debug_and_verbose_can_come_from_env(self):
        os.environ["DEBUG_LOGS"] = "1"
        os.environ["VERBOSE_LOGS"] = "true"

        log, out, _ = self.make_logger(use_color=False, use_icons=False)
        log.log("debug")
        log.info("verbose")

        text = out.getvalue()
        self.assertIn("[Log] debug\n", text)
        self.assertIn("[Info] verbose\n", text)

    def test_style_name_and_custom_overrides_work(self):
        custom = get_style("cli", warn_icon="!", warn_label="[W]")
        self.assertIsInstance(custom, LogStyle)
        self.assertEqual("!", custom.warn_icon)
        self.assertEqual("[W]", custom.warn_label)

        log, out, _ = self.make_logger(use_color=False, use_icons=False, style=custom)
        log.warn("watch")
        self.assertEqual("[W] watch\n", out.getvalue())

    def test_unknown_style_falls_back_to_default(self):
        log, out, _ = self.make_logger(use_color=False, use_icons=False, style="missing-style")
        log.ok("done")
        self.assertEqual("[OK] done\n", out.getvalue())

    def test_icons_are_shown_only_when_output_stream_is_tty(self):
        log, out, _ = self.make_logger(use_color=False, use_icons=True, stream_out=FakeStream(is_tty=False))
        log.ok("done")
        self.assertEqual("[OK] done\n", out.getvalue())

        log, out, _ = self.make_logger(use_color=False, use_icons=True, stream_out=FakeStream(is_tty=True))
        log.ok("done")
        self.assertIn("✅ [OK] done\n", out.getvalue())

    def test_color_is_applied_per_stream_when_tty(self):
        out = FakeStream(is_tty=True)
        err = FakeStream(is_tty=True)
        log, out, err = self.make_logger(use_color=True, use_icons=False, stream_out=out, stream_err=err)

        log.ok("good")
        log.err("bad")

        self.assertIn("\033[", out.getvalue())
        self.assertIn("\033[", err.getvalue())

    def test_no_color_overrides_force_color(self):
        os.environ["NO_COLOR"] = "1"
        os.environ["FORCE_COLOR"] = "1"

        out = FakeStream(is_tty=True)
        log, out, _ = self.make_logger(use_color=True, use_icons=False, stream_out=out)
        log.ok("done")

        self.assertNotIn("\033[", out.getvalue())

    def test_force_color_enables_color_for_non_tty(self):
        os.environ["FORCE_COLOR"] = "1"

        out = FakeStream(is_tty=False)
        log, out, _ = self.make_logger(use_color=True, use_icons=False, stream_out=out)
        log.ok("done")

        self.assertIn("\033[", out.getvalue())

    def test_public_api_exports_expected_names(self):
        self.assertTrue({"default", "classic", "minimal", "cli", "emoji", "plain"}.issubset(STYLES.keys()))


if __name__ == "__main__":
    unittest.main()

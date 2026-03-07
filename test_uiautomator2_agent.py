#!/usr/bin/env python3
"""uiautomator2_agent 单元测试（mock 设备，无需真机）。"""

import argparse
import json
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# 在 import main 之前 patch，避免真的 import u2
import uiautomator2_agent as agent


class TestHelpers(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(agent._ok(), {"ok": True, "result": None})
        self.assertEqual(agent._ok(1), {"ok": True, "result": 1})
        self.assertEqual(agent._ok({"a": 2}), {"ok": True, "result": {"a": 2}})

    def test_err(self):
        self.assertEqual(agent._err("x"), {"ok": False, "error": "x"})
        self.assertEqual(
            agent._err("x", "y"),
            {"ok": False, "error": "x", "detail": "y"},
        )


class TestSelector(unittest.TestCase):
    def test_selector_empty_returns_none(self):
        d = MagicMock()
        args = argparse.Namespace(
            text=None,
            text_contains=None,
            text_starts_with=None,
            description=None,
            resource_id=None,
            class_name=None,
            instance=None,
        )
        self.assertIsNone(agent._selector(d, args))

    def test_selector_text(self):
        d = MagicMock()
        args = argparse.Namespace(
            text="登录",
            text_contains=None,
            text_starts_with=None,
            description=None,
            resource_id=None,
            class_name=None,
            instance=None,
        )
        agent._selector(d, args)
        d.assert_called_once_with(text="登录")

    def test_selector_combined(self):
        d = MagicMock()
        args = argparse.Namespace(
            text="确定",
            text_contains=None,
            text_starts_with=None,
            description=None,
            resource_id="com.example:id/btn",
            class_name="android.widget.Button",
            instance=0,
        )
        agent._selector(d, args)
        d.assert_called_once_with(
            text="确定",
            resourceId="com.example:id/btn",
            className="android.widget.Button",
            instance=0,
        )


class TestCommandsWithMockDevice(unittest.TestCase):
    def setUp(self):
        self.d = MagicMock()

    def test_cmd_click_by_coord(self):
        args = argparse.Namespace(x=100, y=200, long_click=False, double_click=False, duration=0.5, double_duration=0.1)
        out = agent.cmd_click(self.d, args)
        self.d.click.assert_called_once_with(100, 200)
        self.assertEqual(out, {"ok": True, "result": None})

    def test_cmd_click_by_selector(self):
        sel = MagicMock()
        self.d.return_value = sel
        args = argparse.Namespace(
            x=None,
            y=None,
            text="登录",
            text_contains=None,
            text_starts_with=None,
            description=None,
            resource_id=None,
            class_name=None,
            instance=None,
            long_click=False,
            duration=0.5,
        )
        out = agent.cmd_click(self.d, args)
        sel.click.assert_called_once()
        self.assertEqual(out, {"ok": True, "result": None})

    def test_cmd_click_selector_required(self):
        args = argparse.Namespace(
            x=None,
            y=None,
            text=None,
            text_contains=None,
            text_starts_with=None,
            description=None,
            resource_id=None,
            class_name=None,
            instance=None,
        )
        out = agent.cmd_click(self.d, args)
        self.assertFalse(out["ok"])
        self.assertIn("selector_required", out["error"])

    def test_cmd_wait_selector_required(self):
        args = argparse.Namespace(
            text=None,
            text_contains=None,
            description=None,
            resource_id=None,
            class_name=None,
            timeout=10.0,
        )
        out = agent.cmd_wait(self.d, args)
        self.assertFalse(out["ok"])

    def test_cmd_send_keys(self):
        args = argparse.Namespace(value="hello", clear=True)
        out = agent.cmd_send_keys(self.d, args)
        self.d.send_keys.assert_called_once_with("hello", clear=True)
        self.assertTrue(out["ok"])

    def test_cmd_swipe(self):
        args = argparse.Namespace(fx=500, fy=1000, tx=500, ty=300, duration=0.2, steps=None)
        out = agent.cmd_swipe(self.d, args)
        self.d.swipe.assert_called_once_with(500, 1000, 500, 300, duration=0.2, steps=None)
        self.assertTrue(out["ok"])

    def test_cmd_press(self):
        args = argparse.Namespace(key="home")
        out = agent.cmd_press(self.d, args)
        self.d.press.assert_called_once_with("home")
        self.assertTrue(out["ok"])

    def test_cmd_app_start(self):
        args = argparse.Namespace(package="com.example.app", stop=True, activity=None)
        out = agent.cmd_app_start(self.d, args)
        self.d.app_start.assert_called_once_with("com.example.app", stop=True, activity=None)
        self.assertTrue(out["ok"])

    def test_cmd_app_stop(self):
        args = argparse.Namespace(package="com.example.app")
        out = agent.cmd_app_stop(self.d, args)
        self.d.app_stop.assert_called_once_with("com.example.app")
        self.assertTrue(out["ok"])

    def test_cmd_app_current(self):
        self.d.app_current.return_value = {"package": "com.a", "activity": ".Main"}
        args = argparse.Namespace()
        out = agent.cmd_app_current(self.d, args)
        self.assertEqual(out["result"], {"package": "com.a", "activity": ".Main"})

    def test_cmd_screenshot_save(self):
        mock_img = MagicMock()
        self.d.screenshot.return_value = mock_img
        args = argparse.Namespace(output="/tmp/out.png", path=None)
        out = agent.cmd_screenshot(self.d, args)
        mock_img.save.assert_called_once_with("/tmp/out.png")
        self.assertEqual(out["result"]["saved"], "/tmp/out.png")

    def test_cmd_shell(self):
        self.d.shell.return_value = ("output line\n", 0)
        args = argparse.Namespace(cmd="ls /sdcard")
        out = agent.cmd_shell(self.d, args)
        self.d.shell.assert_called_once_with("ls /sdcard")
        self.assertEqual(out["result"]["output"], "output line\n")
        self.assertEqual(out["result"]["exit_code"], 0)

    def test_cmd_window_size(self):
        self.d.window_size.return_value = (1080, 1920)
        args = argparse.Namespace()
        out = agent.cmd_window_size(self.d, args)
        self.assertEqual(out["result"], {"width": 1080, "height": 1920})

    def test_cmd_set_text_selector_required(self):
        args = argparse.Namespace(
            value="hello",
            resource_id=None,
            description=None,
            class_name=None,
        )
        out = agent.cmd_set_text(self.d, args)
        self.assertFalse(out["ok"])


class TestCLI(unittest.TestCase):
    """通过子进程或 patch main 测试 CLI 参数与 JSON 输出。"""

    @patch("uiautomator2_agent._connect")
    def test_cli_help(self, mock_connect):
        with patch.object(sys, "argv", ["uiautomator2_agent.py", "--help"]):
            with self.assertRaises(SystemExit) as ctx:
                agent.main()
            self.assertEqual(ctx.exception.code, 0)

    @patch("uiautomator2_agent._connect")
    def test_cli_window_size_json(self, mock_connect):
        mock_d = MagicMock()
        mock_d.window_size.return_value = (720, 1280)
        mock_connect.return_value = mock_d

        with patch.object(sys, "argv", ["uiautomator2_agent.py", "--json", "window-size"]):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                code = agent.main()
        out = json.loads(stdout.getvalue())
        self.assertEqual(out["ok"], True)
        self.assertEqual(out["result"], {"width": 720, "height": 1280})
        self.assertEqual(code, 0)

    @patch("uiautomator2_agent._connect")
    def test_cli_click_by_text_json(self, mock_connect):
        mock_d = MagicMock()
        mock_sel = MagicMock()
        mock_d.return_value = mock_sel
        mock_connect.return_value = mock_d

        with patch.object(
            sys,
            "argv",
            ["uiautomator2_agent.py", "--json", "--device", "192.168.1.1:5555", "click", "--text", "登录"],
        ):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                code = agent.main()
        mock_connect.assert_called_once_with("192.168.1.1:5555")
        mock_d.assert_called_once_with(text="登录")
        mock_sel.click.assert_called_once()
        out = json.loads(stdout.getvalue())
        self.assertTrue(out["ok"])
        self.assertEqual(code, 0)

    @patch("uiautomator2_agent._connect")
    def test_cli_connect_error_returns_json_error(self, mock_connect):
        mock_connect.side_effect = RuntimeError("device not found")
        with patch.object(sys, "argv", ["uiautomator2_agent.py", "--json", "window-size"]):
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                code = agent.main()
        out = json.loads(stdout.getvalue())
        self.assertFalse(out["ok"])
        self.assertEqual(out["error"], "RuntimeError")
        self.assertIn("device not found", out.get("detail", ""))
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()

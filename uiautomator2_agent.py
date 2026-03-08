#!/usr/bin/env python3
"""
uiautomator2 Agent 脚本 - 便于 Agent 通过 CLI 调用 Android UI 自动化。

用法示例:
  python uiautomator2_agent.py --device 192.168.1.100:5555 click --text "登录"
  python uiautomator2_agent.py swipe 500 1000 500 300 --duration 0.3
  python uiautomator2_agent.py app_start com.example.app
  python uiautomator2_agent.py screenshot --output screen.png

依赖: pip install uiautomator2
"""

import argparse
import json
import sys
from typing import Any, Optional


def _connect(device: Optional[str] = None):
    """连接设备。device 为 None 时连接当前唯一 USB 设备；否则为序列号或 IP:port。"""
    import uiautomator2 as u2
    if device:
        return u2.connect(device)
    return u2.connect()


def _ok(result: Any = None) -> dict:
    return {"ok": True, "result": result}


def _err(message: str, detail: Optional[str] = None) -> dict:
    out = {"ok": False, "error": message}
    if detail:
        out["detail"] = detail
    return out


def cmd_click(d: Any, args: argparse.Namespace) -> dict:
    if args.x is not None and args.y is not None:
        duration = getattr(args, "duration", None) or 0.5
        if getattr(args, "long_click", False):
            d.long_click(args.x, args.y, duration=duration)
        elif getattr(args, "double_click", False):
            d.double_click(args.x, args.y, duration=getattr(args, "double_duration", 0.1))
        else:
            d.click(args.x, args.y)
        return _ok()
    # 选择器点击
    sel = _selector(d, args)
    if sel is None:
        return _err("selector_required", "需要提供 --text / --resource-id / --description / --class-name 或 --x --y")
    if getattr(args, "long_click", False):
        sel.long_click(duration=getattr(args, "duration", 0.5))
    else:
        sel.click()
    return _ok()


def _selector(d: Any, args: argparse.Namespace):
    text = getattr(args, "text", None)
    text_contains = getattr(args, "text_contains", None)
    text_starts = getattr(args, "text_starts_with", None)
    desc = getattr(args, "description", None)
    rid = getattr(args, "resource_id", None)
    clazz = getattr(args, "class_name", None)
    instance = getattr(args, "instance", None)
    kwargs = {}
    if text is not None:
        kwargs["text"] = text
    if text_contains is not None:
        kwargs["textContains"] = text_contains
    if text_starts is not None:
        kwargs["textStartsWith"] = text_starts
    if desc is not None:
        kwargs["description"] = desc
    if rid is not None:
        kwargs["resourceId"] = rid
    if clazz is not None:
        kwargs["className"] = clazz
    if instance is not None:
        kwargs["instance"] = instance
    if not kwargs:
        return None
    return d(**kwargs)


def cmd_wait(d: Any, args: argparse.Namespace) -> dict:
    sel = _selector(d, args)
    if sel is None:
        return _err("selector_required", "需要提供 --text / --resource-id / --description / --class-name 之一")
    timeout = getattr(args, "timeout", 10.0)
    sel.wait(timeout=timeout)
    return _ok()


def cmd_set_text(d: Any, args: argparse.Namespace) -> dict:
    sel = _selector(d, args)
    if sel is None:
        return _err("selector_required", "需要提供选择器以定位输入框")
    text = getattr(args, "value", None) or getattr(args, "text", "")
    sel.set_text(text)
    return _ok()


def cmd_send_keys(d: Any, args: argparse.Namespace) -> dict:
    text = getattr(args, "value", None) or getattr(args, "text", "")
    clear = getattr(args, "clear", False)
    d.send_keys(text, clear=clear)
    return _ok()


def cmd_swipe(d: Any, args: argparse.Namespace) -> dict:
    fx, fy, tx, ty = args.fx, args.fy, args.tx, args.ty
    duration = getattr(args, "duration", 0.1)
    steps = getattr(args, "steps", None)
    d.swipe(fx, fy, tx, ty, duration=duration, steps=steps)
    return _ok()


def cmd_drag(d: Any, args: argparse.Namespace) -> dict:
    duration = getattr(args, "duration", 0.5)
    d.drag(args.sx, args.sy, args.ex, args.ey, duration=duration)
    return _ok()


def cmd_press(d: Any, args: argparse.Namespace) -> dict:
    key = getattr(args, "key", "back")
    d.press(key)
    return _ok()


def cmd_app_start(d: Any, args: argparse.Namespace) -> dict:
    pkg = args.package
    stop = getattr(args, "stop", False)
    activity = getattr(args, "activity", None)
    d.app_start(pkg, stop=stop, activity=activity)
    return _ok()


def cmd_app_stop(d: Any, args: argparse.Namespace) -> dict:
    d.app_stop(args.package)
    return _ok()


def cmd_app_current(d: Any, args: argparse.Namespace) -> dict:
    info = d.app_current()
    return _ok(info)


def cmd_app_wait(d: Any, args: argparse.Namespace) -> dict:
    timeout = getattr(args, "timeout", 20.0)
    front = getattr(args, "front", True)
    d.app_wait(args.package, timeout=timeout, front=front)
    return _ok()


def cmd_screenshot(d: Any, args: argparse.Namespace) -> dict:
    path = getattr(args, "output", None) or getattr(args, "path", None)
    img = d.screenshot()
    if path:
        img.save(path)
        return _ok({"saved": path})
    return _ok({"format": "PIL.Image", "hint": "use --output path to save"})


def cmd_shell(d: Any, args: argparse.Namespace) -> dict:
    output, code = d.shell(args.cmd)
    return _ok({"output": output, "exit_code": code})


def cmd_window_size(d: Any, args: argparse.Namespace) -> dict:
    w, h = d.window_size()
    return _ok({"width": w, "height": h})


def cmd_unlock(d: Any, args: argparse.Namespace) -> dict:
    d.unlock()
    return _ok()


def cmd_pull(d: Any, args: argparse.Namespace) -> dict:
    d.pull(args.remote, args.local)
    return _ok({"local": args.local})


def cmd_push(d: Any, args: argparse.Namespace) -> dict:
    d.push(args.local, args.remote)
    return _ok({"remote": args.remote})


def cmd_session(d: Any, args: argparse.Namespace) -> dict:
    """Session 仅用于同一进程内后续操作，CLI 单次调用中 session 意义有限；这里仅启动应用并返回 ok。"""
    d.app_start(args.package, stop=getattr(args, "stop", False))
    return _ok({"session": args.package})


def main():
    parser = argparse.ArgumentParser(description="uiautomator2 Agent CLI")
    parser.add_argument("--device", "-d", default=None, help="设备: 序列号或 IP:port，省略则连接当前唯一 USB 设备")
    parser.add_argument("--json", action="store_true", help="始终输出 JSON（默认在 stdout 为 TTY 时人类可读）")
    sub = parser.add_subparsers(dest="command", required=True)

    # click
    p_click = sub.add_parser("click", help="点击元素或坐标")
    p_click.add_argument("--x", type=int, default=None, help="点击坐标 x")
    p_click.add_argument("--y", type=int, default=None, help="点击坐标 y")
    p_click.add_argument("--text", default=None)
    p_click.add_argument("--text-contains", dest="text_contains", default=None)
    p_click.add_argument("--text-starts-with", dest="text_starts_with", default=None)
    p_click.add_argument("--description", default=None)
    p_click.add_argument("--resource-id", dest="resource_id", default=None)
    p_click.add_argument("--class-name", dest="class_name", default=None)
    p_click.add_argument("--instance", type=int, default=None)
    p_click.add_argument("--long-click", action="store_true")
    p_click.add_argument("--double-click", action="store_true")
    p_click.add_argument("--duration", type=float, default=0.5)
    p_click.add_argument("--double-duration", type=float, default=0.1)
    p_click.set_defaults(run=cmd_click)

    # wait
    p_wait = sub.add_parser("wait", help="等待元素出现")
    p_wait.add_argument("--text", default=None)
    p_wait.add_argument("--text-contains", dest="text_contains", default=None)
    p_wait.add_argument("--description", default=None)
    p_wait.add_argument("--resource-id", dest="resource_id", default=None)
    p_wait.add_argument("--class-name", dest="class_name", default=None)
    p_wait.add_argument("--timeout", type=float, default=10.0)
    p_wait.set_defaults(run=cmd_wait)

    # set_text
    p_set = sub.add_parser("set-text", help="在匹配的输入框中设置文本")
    p_set.add_argument("--text", "--value", dest="value", required=True)
    p_set.add_argument("--resource-id", dest="resource_id", default=None)
    p_set.add_argument("--description", default=None)
    p_set.add_argument("--class-name", dest="class_name", default=None)
    p_set.set_defaults(run=cmd_set_text)

    # send_keys
    p_send = sub.add_parser("send-keys", help="向当前焦点输入文本")
    p_send.add_argument("--text", "--value", dest="value", required=True)
    p_send.add_argument("--clear", action="store_true")
    p_send.set_defaults(run=cmd_send_keys)

    # swipe
    p_swipe = sub.add_parser("swipe", help="滑动 (fx fy tx ty)")
    p_swipe.add_argument("fx", type=int)
    p_swipe.add_argument("fy", type=int)
    p_swipe.add_argument("tx", type=int)
    p_swipe.add_argument("ty", type=int)
    p_swipe.add_argument("--duration", type=float, default=0.1)
    p_swipe.add_argument("--steps", type=int, default=None)
    p_swipe.set_defaults(run=cmd_swipe)

    # drag
    p_drag = sub.add_parser("drag", help="拖拽 (sx sy ex ey)")
    p_drag.add_argument("sx", type=int)
    p_drag.add_argument("sy", type=int)
    p_drag.add_argument("ex", type=int)
    p_drag.add_argument("ey", type=int)
    p_drag.add_argument("--duration", type=float, default=0.5)
    p_drag.set_defaults(run=cmd_drag)

    # press
    p_press = sub.add_parser("press", help="按键 (home/back/menu/enter/recent/volume_up/volume_down/power 等)")
    p_press.add_argument("key", nargs="?", default="back")
    p_press.set_defaults(run=cmd_press)

    # back：等同于 press back，方便无实体 Back 键时用 CLI 模拟
    sub.add_parser("back", help="按 Back 键（等同于 press back）").set_defaults(run=cmd_press, key="back")

    # app_start
    p_start = sub.add_parser("app-start", help="启动应用")
    p_start.add_argument("package", help="包名")
    p_start.add_argument("--stop", action="store_true", help="先结束再启动")
    p_start.add_argument("--activity", default=None)
    p_start.set_defaults(run=cmd_app_start)

    # app_stop
    p_stop = sub.add_parser("app-stop", help="停止应用")
    p_stop.add_argument("package")
    p_stop.set_defaults(run=cmd_app_stop)

    # app_current
    sub.add_parser("app-current", help="当前前台应用").set_defaults(run=cmd_app_current)

    # app_wait
    p_await = sub.add_parser("app-wait", help="等待应用启动")
    p_await.add_argument("package")
    p_await.add_argument("--timeout", type=float, default=20.0)
    p_await.add_argument("--front", type=lambda x: x.lower() == "true", default=True)
    p_await.set_defaults(run=cmd_app_wait)

    # screenshot
    p_shot = sub.add_parser("screenshot", help="截图")
    p_shot.add_argument("--output", "--path", dest="output", default=None)
    p_shot.set_defaults(run=cmd_screenshot)

    # shell
    p_shell = sub.add_parser("shell", help="执行 adb shell 命令")
    p_shell.add_argument("cmd", nargs="+", help="命令与参数")
    def _shell_run(d, a):
        cmd = a.cmd if isinstance(a.cmd, str) else " ".join(a.cmd)
        return cmd_shell(d, argparse.Namespace(cmd=cmd))
    p_shell.set_defaults(run=_shell_run)

    # window_size
    sub.add_parser("window-size", help="屏幕宽高").set_defaults(run=cmd_window_size)

    # unlock
    sub.add_parser("unlock", help="解锁屏幕").set_defaults(run=cmd_unlock)

    # pull / push
    p_pull = sub.add_parser("pull", help="从设备拉取文件")
    p_pull.add_argument("remote", help="设备路径")
    p_pull.add_argument("local", help="本地路径")
    p_pull.set_defaults(run=cmd_pull)

    p_push = sub.add_parser("push", help="推送文件到设备")
    p_push.add_argument("local", help="本地路径")
    p_push.add_argument("remote", help="设备路径")
    p_push.set_defaults(run=cmd_push)

    args = parser.parse_args()
    use_json = args.json or not sys.stdout.isatty()

    try:
        d = _connect(args.device)
        out = args.run(d, args)
    except Exception as e:
        out = _err(type(e).__name__, str(e))

    if use_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if out.get("ok"):
            r = out.get("result")
            if r is not None:
                print(json.dumps(r, ensure_ascii=False, indent=2))
            else:
                print("ok")
        else:
            print("error:", out.get("error"), out.get("detail", ""), file=sys.stderr)
            sys.exit(1)
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

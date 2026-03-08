---
name: uiautomator-android-cli
description: Connect to Android device and run low-level actions (click, swipe, app-start, screenshot, etc.) via uiautomator_android_cli.py. For Android UI automation, uiautomator2, and atx-agent.
---

# uiautomator_android_cli usage

This layer corresponds to **UIAutomatorAndroid**, handling device connection and basic actions. See `requirements.txt` for dependencies.

## How to run

From the `uiautomator_android` directory, or with this directory and its dependencies on the Python path:

```bash
python uiautomator_android_cli.py --help
python uiautomator_android_cli.py --device 192.168.1.100:5555 click --text "登录"
python uiautomator_android_cli.py app-start com.xunmeng.pinduoduo
python uiautomator_android_cli.py swipe 500 1000 500 300 --duration 0.3
python uiautomator_android_cli.py screenshot --output screen.png
python uiautomator_android_cli.py dump   # if supported
```

You can also use `uiautomator2_agent.py` in the same directory (same implementation as the CLI).

## Common subcommands

| Subcommand | Description |
|------------|-------------|
| `click` | Click (--text / --resource-id / --x --y) |
| `wait` | Wait for element (--timeout) |
| `set-text` | Set text in input |
| `send-keys` | Type at current focus |
| `swipe` | Swipe fx fy tx ty |
| `drag` | Drag |
| `press` | Key press (back/home/menu, etc.) |
| `app-start` | Start app (package [--stop] [--activity]) |
| `app-stop` | Stop app |
| `app-current` | Current foreground app |
| `app-wait` | Wait for app to start |
| `screenshot` | Screenshot (--output path) |
| `shell` | adb shell |
| `window-size` | Screen width/height |
| `unlock` | Unlock |
| `pull` / `push` | Pull/push files |

## Global options

- `--device`, `-d`: Device serial or `IP:port`; omit to use the only USB device.
- `--json`: Output JSON.

## Dependencies

See `requirements.txt` (e.g. `uiautomator2`). Device must have atx-agent (usually `python -m uiautomator2 init` once).

---
name: uiautomator-android-cli
description: 通过 uiautomator_android_cli.py 连接 Android 设备并执行原子操作（click、swipe、app-start、screenshot 等）。适用于 Android UI 自动化、uiautomator2、atx-agent 场景。
---

# uiautomator_android_cli 用法

本层对应 **UIAutomatorAndroid**，负责连接设备与基础原子操作。依赖见 `requirements.txt`。

## 运行方式

在 `uiautomator_android` 目录下，或已将本目录与依赖加入 Python 路径时：

```bash
python uiautomator_android_cli.py --help
python uiautomator_android_cli.py --device 192.168.1.100:5555 click --text "登录"
python uiautomator_android_cli.py app-start com.xunmeng.pinduoduo
python uiautomator_android_cli.py swipe 500 1000 500 300 --duration 0.3
python uiautomator_android_cli.py screenshot --output screen.png
python uiautomator_android_cli.py dump   # 若支持
```

也可直接使用同目录下的 `uiautomator2_agent.py`（与 `uiautomator_android_cli.py` 同一实现）。

## 常用子命令

| 子命令 | 说明 |
|--------|------|
| `click` | 点击（--text / --resource-id / --x --y） |
| `wait` | 等待元素（--timeout） |
| `set-text` | 在输入框设文本 |
| `send-keys` | 当前焦点输入 |
| `swipe` | 滑动 fx fy tx ty |
| `drag` | 拖拽 |
| `press` | 按键 back/home/menu 等 |
| `app-start` | 启动应用（package [--stop] [--activity]） |
| `app-stop` | 停止应用 |
| `app-current` | 当前前台应用 |
| `app-wait` | 等待应用启动 |
| `screenshot` | 截图（--output path） |
| `shell` | adb shell |
| `window-size` | 屏幕宽高 |
| `unlock` | 解锁 |
| `pull` / `push` | 文件拉取/推送 |

## 全局参数

- `--device`, `-d`：设备序列号或 `IP:port`，省略则连接当前唯一 USB 设备。
- `--json`：输出 JSON。

## 依赖

见 `requirements.txt`（如 `uiautomator2`）。设备需已运行 atx-agent（通常 `python -m uiautomator2 init` 一次即可）。

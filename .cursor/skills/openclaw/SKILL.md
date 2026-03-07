---
name: openclaw
description: Supports basic uiautomator2 operations for Android UI automation. Use when writing or debugging scripts with uiautomator2, Android device automation, openclaw, or when the user needs connect, click, swipe, input, selector, or app control with uiautomator2.
---

# OpenClaw – uiautomator2 基本操作

本 skill 指导在 Python 中使用 uiautomator2 进行 Android UI 自动化的基本操作。依赖：`pip install uiautomator2`，设备需已运行 atx-agent（通常 `python -m uiautomator2 init` 一次即可）。

## 连接设备

```python
import uiautomator2 as u2

# USB：自动连接当前唯一设备
d = u2.connect()

# USB：指定序列号
d = u2.connect("serial_no")

# WiFi：IP:port（默认 5555）
d = u2.connect("192.168.1.100:5555")
```

## 元素选择器（Selector）

通过 `d(条件)` 得到元素，再在其上操作。常用条件：

| 条件 | 示例 |
|------|------|
| text | `d(text="登录")` |
| textContains | `d(textContains="登")` |
| textStartsWith | `d(textStartsWith="登")` |
| description | `d(description="设置")` |
| resourceId | `d(resourceId="com.example:id/btn_ok")` |
| className | `d(className="android.widget.Button")` |
| 组合 | `d(text="确定", className="android.widget.Button")` |

可用链式：`d(...).child(text="子文本")`、`.sibling()`、`.left()`, `.right()`, `.up()`, `.down()` 等做相对定位。

## 点击与坐标操作

```python
# 按元素点击
d(text="登录").click()
d(description="设置").click()

# 按坐标点击（Session/Device 均可）
d.click(x, y)   # 或 d.tap(x, y)
d.long_click(x, y, duration=0.5)
d.double_click(x, y, duration=0.1)
```

## 输入文本

```python
# 在匹配的输入框内设文本（会先点击聚焦）
d(resourceId="com.example:id/username").set_text("hello")

# 全局输入（当前焦点），可选先清空
d.send_keys("hello world", clear=False)
```

## 滑动与拖拽

```python
# 坐标均为像素；(fx,fy) -> (tx,ty)
d.swipe(fx, fy, tx, ty, duration=0.1, steps=None)
d.drag(sx, sy, ex, ey, duration=0.5)

# 多点滑动
d.swipe_points([[x1,y1], [x2,y2], [x3,y3]], duration=0.5)
```

## 按键

```python
d.press("home")       # home, back, left, right, up, down, center
d.press("back")
d.press("menu")
d.press("enter")
d.press("recent")     # 最近任务
d.press("volume_up")  # volume_down, volume_mute
d.press("power")
```

## 应用生命周期

```python
# 启动
d.app_start("com.example.app", stop=True)   # stop=True 先结束再启动
d.app_start("com.example.app", activity=".MainActivity")

# 停止
d.app_stop("com.example.app")

# 当前前台应用
info = d.app_current()   # {"package": "...", "activity": "..."}

# 等待应用启动
d.app_wait("com.example.app", timeout=20.0, front=True)
```

## 截图与等待

```python
# 截图：返回 PIL.Image，可保存
img = d.screenshot()
img.save("screen.png")

# 等待元素出现再操作
d(text="加载中").wait(timeout=10.0)
d(text="确定").click()
```

## 其他常用

```python
# 屏幕尺寸
w, h = d.window_size()

# 解屏
d.unlock()

# 拉取/推送文件
d.pull("/sdcard/xxx.txt", "./local.txt")
d.push("./local.txt", "/sdcard/xxx.txt")

# Shell
output, code = d.shell("ls /sdcard")
```

## 会话（Session）—— 限定在当前应用内

需要所有操作限定在某个应用内时，使用 session：

```python
s = d.session("com.example.app")
s.click(100, 200)
s.swipe(500, 1000, 500, 300)
s.send_keys("input text")
s.screenshot("screen.jpg")
# 按键、drag 等与 Device 类似
```

## 编写脚本时的注意点

1. **先等再点**：界面未就绪时用 `d(selector).wait(timeout=10)` 再 `click()`。
2. **异常**：连接失败、元素未找到等会抛异常，用 try/except 或重试。
3. **输入法**：`set_text` 依赖 atx FastInputIME；若无效可检查 `d.set_fastinput_ime(True)` 或改用 `send_keys`。
4. **稳定性**：关键步骤后可加短 `time.sleep()` 或 `wait()`，避免动画未结束就操作。

## 参考

- 完整 API：<https://uiautomator2.readthedocs.io/en/latest/api.html>
- 更多示例见 [reference.md](reference.md)（可选）。

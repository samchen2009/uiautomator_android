# uiautomator2 参考

## 更多选择器示例

```python
# 子节点 / 兄弟节点
d(className="android.widget.ListView").child(text="选项A").click()
d(text="标题").sibling(className="android.widget.Button").click()

# 通过索引
d(className="android.widget.Button", instance=0).click()  # 第一个 Button
```

## Device 常用方法速查

| 方法 | 说明 |
|------|------|
| `app_current()` | 当前前台 package/activity |
| `app_start(pkg, activity=..., stop=...)` | 启动应用 |
| `app_stop(pkg)` | 停止应用 |
| `app_wait(pkg, timeout=..., front=...)` | 等待应用启动 |
| `click(x,y)` / `tap(x,y)` | 坐标点击 |
| `pull(src, dst)` / `push(src, dst)` | 文件拉取/推送 |
| `screenshot()` | 截图，返回 PIL.Image |
| `shell(cmd)` | 执行 adb shell，返回 (output, exit_code) |
| `swipe(fx,fy,tx,ty,...)` / `drag(...)` | 滑动/拖拽 |
| `unlock()` | 解锁屏幕 |
| `window_size()` | (width, height) |

## Session 常用方法速查

| 方法 | 说明 |
|------|------|
| `click(x,y)` / `long_click` / `double_click` | 坐标点击 |
| `send_keys(text, clear=False)` | 输入文本 |
| `swipe` / `drag` / `swipe_points` | 滑动 |
| `screenshot(filename=...)` | 截图 |
| `press(key)` | 按键 |

## 官方文档

- API: https://uiautomator2.readthedocs.io/en/latest/api.html

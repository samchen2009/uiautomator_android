"""
UIAutomatorAndroid：实现统一设备驱动接口，使用 uiautomator2 连接设备。
供 UIAutomator.init() 自动检测时使用，或由调用方直接注入。
"""

import time
from typing import Any, List, Optional

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None


def _ok(result: Any = None) -> dict:
    return {"ok": True, "result": result}


def _err(error: str, detail: Optional[str] = None) -> dict:
    out: dict = {"ok": False, "error": error}
    if detail is not None:
        out["detail"] = detail
    return out


def _selector_kwargs(
    *,
    text: Optional[str] = None,
    text_contains: Optional[str] = None,
    resource_id: Optional[str] = None,
    description: Optional[str] = None,
    class_name: Optional[str] = None,
    instance: Optional[int] = None,
) -> dict:
    kwargs = {}
    if text is not None:
        kwargs["text"] = text
    if text_contains is not None:
        kwargs["textContains"] = text_contains
    if resource_id is not None:
        kwargs["resourceId"] = resource_id
    if description is not None:
        kwargs["description"] = description
    if class_name is not None:
        kwargs["className"] = class_name
    if instance is not None:
        kwargs["instance"] = instance
    return kwargs


class UIAutomatorAndroid:
    """实现 UiautomatorDriver 接口，底层使用 uiautomator2；方法返回 self，结果从 last_result 取。"""

    def __init__(self, device: Optional[str] = None) -> None:
        self._device = device
        self._d: Any = None
        self._last_result: dict = _ok()

    @property
    def last_result(self) -> dict:
        """上次调用的结果。"""
        return self._last_result

    def connect(self) -> dict:
        """连接设备。device 为 None 时连接当前唯一 USB 设备；否则为序列号或 IP:port。"""
        if u2 is None:
            return _err("ImportError", "uiautomator2 未安装")
        try:
            if self._device:
                self._d = u2.connect(self._device)
            else:
                self._d = u2.connect()
            return _ok()
        except Exception as e:
            return _err(type(e).__name__, str(e))

    def _ensure(self) -> Any:
        if self._d is None:
            raise RuntimeError("UIAutomatorAndroid 未连接，请先调用 connect()")
        return self._d

    def click(
        self,
        *,
        x: Optional[int] = None,
        y: Optional[int] = None,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
        instance: Optional[int] = None,
    ) -> "UIAutomatorAndroid":
        d = self._ensure()
        try:
            if x is not None and y is not None:
                d.click(x, y)
                self._last_result = _ok()
            else:
                kw = _selector_kwargs(
                    text=text, text_contains=text_contains,
                    resource_id=resource_id, description=description,
                    class_name=class_name, instance=instance,
                )
                if not kw:
                    self._last_result = _err("selector_required", "需要提供坐标或选择器")
                else:
                    d(**kw).click()
                    self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def longpress(
        self,
        *,
        x: Optional[int] = None,
        y: Optional[int] = None,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
        instance: Optional[int] = None,
        duration: float = 0.5,
    ) -> "UIAutomatorAndroid":
        """长按（坐标或选择器），duration 为按住时长（秒）。"""
        d = self._ensure()
        try:
            if x is not None and y is not None:
                d.long_click(x, y, duration=duration)
                self._last_result = _ok()
            else:
                kw = _selector_kwargs(
                    text=text, text_contains=text_contains,
                    resource_id=resource_id, description=description,
                    class_name=class_name, instance=instance,
                )
                if not kw:
                    self._last_result = _err("selector_required", "需要提供坐标或选择器")
                else:
                    d(**kw).long_click(duration=duration)
                    self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def wait(
        self,
        *,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
        timeout: float = 10.0,
    ) -> "UIAutomatorAndroid":
        d = self._ensure()
        kw = _selector_kwargs(
            text=text, text_contains=text_contains,
            resource_id=resource_id, description=description,
            class_name=class_name,
        )
        if not kw:
            self._last_result = _err("selector_required", "需要提供选择器")
            return self
        try:
            d(**kw).wait(timeout=timeout)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def set_text(
        self,
        value: str,
        *,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> "UIAutomatorAndroid":
        d = self._ensure()
        kw = _selector_kwargs(
            resource_id=resource_id, description=description,
            class_name=class_name,
        )
        if not kw:
            self._last_result = _err("selector_required", "需要提供选择器以定位输入框")
            return self
        try:
            d(**kw).set_text(value)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def send_keys(self, value: str, *, clear: bool = False) -> "UIAutomatorAndroid":
        try:
            self._ensure().send_keys(value, clear=clear)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def swipe(
        self,
        fx: int,
        fy: int,
        tx: int,
        ty: int,
        *,
        duration: float = 0.1,
        steps: Optional[int] = None,
    ) -> "UIAutomatorAndroid":
        try:
            self._ensure().swipe(fx, fy, tx, ty, duration=duration, steps=steps)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def drag(
        self,
        sx: int,
        sy: int,
        ex: int,
        ey: int,
        *,
        duration: float = 0.5,
    ) -> "UIAutomatorAndroid":
        try:
            self._ensure().drag(sx, sy, ex, ey, duration=duration)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def press(self, key: str = "back") -> "UIAutomatorAndroid":
        try:
            self._ensure().press(key)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def app_start(
        self,
        package: str,
        *,
        stop: bool = False,
        activity: Optional[str] = None,
        uri: Optional[str] = None,
    ) -> "UIAutomatorAndroid":
        try:
            d = self._ensure()
            if uri:
                output, code = d.shell("am start -a android.intent.action.VIEW -d " + repr(uri) + " -p " + repr(package))
                if code != 0:
                    self._last_result = _err("app_start_uri_failed", output or str(code))
                else:
                    self._last_result = _ok()
            else:
                d.app_start(package, stop=stop, activity=activity)
                self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def app_stop(self, package: str) -> "UIAutomatorAndroid":
        try:
            self._ensure().app_stop(package)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def app_current(self) -> "UIAutomatorAndroid":
        try:
            info = self._ensure().app_current()
            self._last_result = _ok(info)
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def app_wait(
        self,
        package: str,
        *,
        timeout: float = 20.0,
        front: bool = True,
    ) -> "UIAutomatorAndroid":
        try:
            self._ensure().app_wait(package, timeout=timeout, front=front)
            self._last_result = _ok()
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def screenshot(self, *, path: Optional[str] = None) -> "UIAutomatorAndroid":
        try:
            img = self._ensure().screenshot()
            if path:
                img.save(path)
                self._last_result = _ok({"saved": path})
            else:
                self._last_result = _ok({"format": "PIL.Image", "hint": "use path= to save"})
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def window_size(self) -> "UIAutomatorAndroid":
        try:
            w, h = self._ensure().window_size()
            self._last_result = _ok({"width": w, "height": h})
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def shell(self, cmd: str) -> "UIAutomatorAndroid":
        try:
            output, code = self._ensure().shell(cmd)
            self._last_result = _ok({"output": output, "exit_code": code})
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def dump(
        self,
        *,
        format: Optional[str] = None,
        mode: str = "current",
        scroll_count: int = 3,
        no_new_limit: int = 5,
        end_marker: Optional[str] = None,
    ) -> "UIAutomatorAndroid":
        """
        层级 dump；结果在 last_result。
        mode:
          - current: 只 dump 当前可见页（默认）。用途：明确目标信息就在当前页。
          - all: 不停下滑到底，每次 dump，直到连续 no_new_limit 次无新内容或出现 end_marker。用途：目标信息是全部。
          - several: 下滑 scroll_count 次，每次 dump。用途：目标信息可能需要滑几次。
        several/all 时 last_result.result 含 xml（最后一屏）和 xml_list（按顺序的完整列表）。
        """
        try:
            d = self._ensure()
            fmt = format or "xml"
            if mode == "current":
                xml = d.dump_hierarchy()
                self._last_result = _ok({"xml": xml, "format": fmt, "mode": "current"})
                return self
            # several / all：需要滑动并多次 dump
            try:
                w, h = d.window_size()
            except Exception:
                w, h = 540, 960
            fx, fy = w // 2, int(h * 0.75)
            tx, ty = w // 2, int(h * 0.25)
            xml_list: List[str] = []
            prev_len = 0
            no_new_count = 0
            while True:
                xml = d.dump_hierarchy()
                xml_list.append(xml)
                if mode == "several":
                    if len(xml_list) >= scroll_count:
                        break
                    d.swipe(fx, fy, tx, ty, duration=0.2)
                    time.sleep(0.8)
                    continue
                # mode == "all"
                if end_marker and end_marker in xml:
                    break
                cur_len = len(xml)
                if cur_len <= prev_len and prev_len > 0:
                    no_new_count += 1
                    if no_new_count >= no_new_limit:
                        break
                else:
                    no_new_count = 0
                prev_len = cur_len
                d.swipe(fx, fy, tx, ty, duration=0.2)
                time.sleep(0.8)
            self._last_result = _ok({
                "xml": xml_list[-1] if xml_list else "",
                "xml_list": xml_list,
                "format": fmt,
                "mode": mode,
            })
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def element_exists(
        self,
        *,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
        timeout: float = 0,
    ) -> "UIAutomatorAndroid":
        """元素是否存在。timeout=0 表示立即检查；结果在 last_result。"""
        d = self._ensure()
        kw = _selector_kwargs(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            description=description,
            class_name=class_name,
        )
        if not kw:
            self._last_result = _err("selector_required", "需要提供选择器")
            return self
        try:
            import time
            if timeout <= 0:
                self._last_result = _ok(bool(d(**kw).exists))
            else:
                deadline = time.monotonic() + timeout
                while time.monotonic() < deadline:
                    if d(**kw).exists:
                        self._last_result = _ok(True)
                        return self
                    time.sleep(0.2)
                self._last_result = _ok(False)
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def get_text(
        self,
        *,
        text: Optional[str] = None,
        text_contains: Optional[str] = None,
        resource_id: Optional[str] = None,
        description: Optional[str] = None,
        class_name: Optional[str] = None,
    ) -> "UIAutomatorAndroid":
        """取匹配元素的文本；结果在 last_result。"""
        d = self._ensure()
        kw = _selector_kwargs(
            text=text,
            text_contains=text_contains,
            resource_id=resource_id,
            description=description,
            class_name=class_name,
        )
        if not kw:
            self._last_result = _err("selector_required", "需要提供选择器")
            return self
        try:
            sel = d(**kw)
            if not sel.exists:
                self._last_result = _ok(None)
            else:
                info = sel.info
                value = (info or {}).get("text") or (info or {}).get("contentDescription")
                self._last_result = _ok(value)
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

    def get_window_name(self) -> "UIAutomatorAndroid":
        """窗口/页面标识；结果在 last_result。"""
        try:
            cur = self._ensure().app_current()
            if not cur:
                self._last_result = _ok(None)
            else:
                self._last_result = _ok(cur.get("activity") or cur.get("package") or str(cur))
        except Exception as e:
            self._last_result = _err(type(e).__name__, str(e))
        return self

#!/usr/bin/env python3
"""
uiautomator_android 命令行入口：调用 UIAutomatorAndroid 能力（连接设备、click、swipe、app_start 等）。
与 uiautomator2_agent 同一实现，本文件为统一命名入口。
"""
from uiautomator2_agent import main

if __name__ == "__main__":
    import sys
    sys.exit(main())

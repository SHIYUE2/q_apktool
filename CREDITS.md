# QApkTool 鸣谢文档

QApkTool 是一个基于开源项目的 APK 反编译 / 回编译对小白友好的图形化工具。本工具的实现离不开以下开源项目和技术贡献，在此致以诚挚的感谢。

---

## 核心依赖

### Apktool

- **项目地址：** https://github.com/iBotPeaches/Apktool
- **作者：** Connor Tumbleson (iBotPeaches)
- **许可证：** Apache License 2.0
- **当前使用版本：** 3.0.2

Apktool 是本工具的核心引擎，负责 APK 文件的反编译（解码资源、smali 代码）与回编译（重新打包）。感谢 Connor Tumbleson 及所有贡献者长期维护这一优秀项目，使得 Android 逆向工程变得更加便捷。

### OpenJDK (Microsoft Build)

- **项目地址：** https://github.com/microsoft/openjdk
- **许可证：** GNU General Public License v2.0 (with Classpath Exception)
- **当前使用版本：** 21.0.7 LTS

Apktool 依赖 Java 运行时执行，本工具内嵌了 Microsoft 构建的 OpenJDK 21 LTS，感谢 Microsoft 及 OpenJDK 社区提供稳定可靠的 Java 运行环境。

### Python

- **项目地址：** https://www.python.org/
- **许可证：** Python Software Foundation License
- **当前使用版本：** 3.10.0

本工具的图形界面由 Python 编写，感谢 Python Software Foundation 提供简洁易用的编程语言和标准库。

---

## 使用的库与框架

### Tkinter (Tk)

Python 标准库自带的 GUI 工具包，基于 Tcl/Tk。本工具的整个用户界面均使用 Tkinter 构建，感谢 Tcl/Tk 和 Tkinter 开发者提供轻量级跨平台 GUI 支持。

### PyInstaller

- **项目地址：** https://github.com/pyinstaller/pyinstaller
- **许可证：** GNU General Public License v2.0

本工具的 Windows 可执行文件（QApkTool.exe）由 PyInstaller 打包生成，感谢 PyInstaller 团队使 Python 应用的独立分发变得简单。

---

## 致谢

感谢所有参与上述开源项目开发、测试、文档编写的贡献者。开源社区的协作精神是本项目得以实现的基础。

如有遗漏，欢迎补充。

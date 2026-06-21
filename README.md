# QApkTool

**APK 反编译 / 回编译一键工具**

QApkTool 是基于 [Apktool](https://github.com/iBotPeaches/Apktool) 的 Windows 图形化封装，提供 APK 文件的反编译（`d`）与回编译（`b`）一键操作，内置 Java 运行环境与 Python 解释器，解压即用，无需额外配置。

## 功能特性

- 支持 APK 反编译（解码 smali 代码与资源文件）
- 支持反编译后文件夹回编译为 APK
- 可选参数：覆盖已有（`-f`）、跳过源码（`--no-src`）、跳过资源（`--no-res`）
- 实时运行日志输出
- 自带 OpenJDK 21 LTS 与 Python 3.10，开箱即用
- 配置自动保存，下次启动无需重新设置路径

## 技术栈

| 组件 | 版本 |
|---|---|
| Apktool | 3.0.2 |
| OpenJDK (Microsoft Build) | 21.0.7 LTS |
| Python | 3.10.0 |
| GUI 框架 | Tkinter |
| 打包工具 | PyInstaller |

## 使用方法

双击 `QApkTool.exe` 或运行 `QApkTool.bat` 启动程序。

### 反编译

1. 切换到「反编译 (d)」标签页
2. 选择要反编译的 APK 文件
3. 可选指定输出目录，留空则自动生成
4. 按需勾选参数，点击「开始反编译」

### 回编译

1. 切换到「回编译 (b)」标签页
2. 选择反编译后生成的文件夹
3. 可选指定输出 APK 路径
4. 点击「开始回编译」

## 项目结构

```
QApkTool/
├── QApkTool.exe      # 主程序（PyInstaller 打包）
├── qapktool.py       # GUI 源码
├── apktool.jar       # Apktool 核心
├── config.json       # 自动生成的配置文件
├── icon.ico          # 图标
├── icon.png
├── jre/              # 内置 OpenJDK 21
├── python/           # 内置 Python 3.10
├── README.md
└── CREDITS.md        # 鸣谢文档
```

## 致谢

详见 [CREDITS.md](CREDITS.md)。

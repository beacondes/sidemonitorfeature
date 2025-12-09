# Windows 11 触控音量控制器

这是一个轻量级的桌面音量控制程序，专为Windows 11触屏设备设计，支持触控滑动调节音量和一键静音功能。

## 功能特点

- 垂直滑动条设计，便于触屏操作
- 一键静音/取消静音
- 半透明界面，美观不遮挡
- 可拖拽移动位置
- 支持Windows 11触屏手势
- 窗口始终保持置顶
- 记住上次退出时的位置和音量设置

## 安装要求

- Python 3.6+
- Windows 11 操作系统

## 安装步骤

1. 安装必要的Python包：
```cmd
pip install PyQt5 pycaw pywin32
```

2. 下载 `DesktopVolumeControl.py` 文件

3. 运行程序：
```cmd
python DesktopVolumeControl.py
```

## 使用方法

- 拖拽顶部区域可移动整个控件
- 上下滑动音量条调节系统音量
- 点击静音按钮（ 🔇 ）切换静音状态

## 技术细节

该程序使用了以下技术：
- PyQt5：用于创建图形界面和处理触控事件
- pycaw：用于Windows音频系统控制
- pywin32：用于窗口管理
- Windows Core Audio API：直接控制系统音量

## 注意事项

- 首次运行可能需要管理员权限才能控制系统音量
- 程序会自动保持在屏幕最顶层
- 适用于Windows 11触屏设备优化

## 自定义配置

可通过修改代码中的以下参数来自定义：
- 界面大小和位置
- 颜色主题
- 初始音量值

程序会在用户目录下创建 `.volume_control_settings.json` 文件来保存以下信息：
- 窗口位置 (window_x, window_y)
- 当前音量值 (volume)
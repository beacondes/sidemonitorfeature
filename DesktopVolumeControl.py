import sys
import os
import json
import platform
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QPushButton, QLabel
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen

# 根据操作系统导入相应的模块
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import winsound
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        from ctypes import cast, POINTER
    except ImportError:
        AudioUtilities = None
else:
    # 在非Windows系统上模拟音量控制功能
    AudioUtilities = None

class VolumeControl(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.expanduser("~"), ".volume_control_settings.json")
        self.load_settings()
        self.init_ui()
        self.set_window_properties()
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)
        
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 静音按钮
        self.mute_button = QPushButton("🔇")
        self.mute_button.setFixedSize(50, 40)
        self.mute_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                border: 2px solid #555;
                border-radius: 8px;
                background-color: #333;
                color: white;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)
        self.mute_button.clicked.connect(self.toggle_mute)
        
        # 音量滑块
        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        
        # 使用加载的初始音量值，如果没有则使用系统音量
        if self.initial_volume is not None:
            self.volume_slider.setValue(self.initial_volume)
            # 同时设置系统音量为保存的值
            self.set_system_volume(self.initial_volume)
        else:
            self.volume_slider.setValue(self.get_system_volume())
        self.volume_slider.setStyleSheet("""
            QSlider::groove:vertical {
                border: 2px solid #555;
                border-radius: 5px;
                width: 20px;
                background: #333;
            }
            QSlider::handle:vertical {
                background: #fff;
                border: 2px solid #555;
                border-radius: 5px;
                width: 24px;
                margin: -2px 0;
            }
            QSlider::add-page:vertical {
                background: #4CAF50;
            }
            QSlider::sub-page:vertical {
                background: #2196F3;
            }
        """)
        self.volume_slider.valueChanged.connect(self.set_system_volume)
        
        # 音量数值显示
        self.volume_label = QLabel(f"{self.volume_slider.value()}%")
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.volume_label.setFixedHeight(25)
        
        # 添加组件到布局
        layout.addWidget(self.mute_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.volume_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.volume_slider)
        
        self.setLayout(layout)
        
        # 设置初始位置（从设置中加载或默认右上角）
        screen_geometry = QApplication.desktop().screenGeometry()
        if hasattr(self, 'window_x') and hasattr(self, 'window_y'):
            self.setGeometry(self.window_x, self.window_y, 70, 200)
        else:
            self.setGeometry(screen_geometry.width() - 80, 50, 70, 200)
        
        self.is_muted = False
        self.original_volume = self.volume_slider.value()

    def set_window_properties(self):
        if platform.system() == "Windows":
            # 设置窗口始终置顶
            hwnd = self.winId().__int__()
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
    def get_system_volume(self):
        if platform.system() == "Windows" and AudioUtilities:
            try:
                # 使用pycaw获取系统音量
                sessions = AudioUtilities.GetAllSessions()
                for session in sessions:
                    volume = session.SimpleAudioVolume
                    if session.Process and session.Process.ProcessName() == "explorer.exe":
                        return int(volume.GetMasterVolume() * 100)
                
                # 如果无法获取特定应用音量，获取系统主音量
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                return int(volume.GetMasterVolumeLevelScalar() * 100)
            except:
                pass
        # 模拟模式下返回默认值
        return 50
    
    def set_system_volume(self, value):
        if platform.system() == "Windows" and AudioUtilities:
            try:
                # 使用pycaw设置系统音量
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(value / 100, None)
            except:
                pass
        else:
            # 在非Windows系统上，仅更新UI
            pass
            
        self.volume_label.setText(f"{value}%")
    
    def toggle_mute(self):
        if platform.system() == "Windows" and AudioUtilities:
            try:
                # 使用pycaw进行静音控制
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                if not self.is_muted:
                    # 保存当前音量并静音
                    self.original_volume = int(volume.GetMasterVolumeLevelScalar() * 100)
                    volume.SetMasterVolumeLevelScalar(0, None)
                    self.volume_slider.setValue(0)
                    self.mute_button.setText("🔊")
                    self.is_muted = True
                else:
                    # 恢复之前的音量
                    volume.SetMasterVolumeLevelScalar(self.original_volume / 100, None)
                    self.volume_slider.setValue(self.original_volume)
                    self.mute_button.setText("🔇")
                    self.is_muted = False
            except:
                # 如果pycaw失败，回退到UI操作
                self.toggle_mute_fallback()
        else:
            # 非Windows系统或pycaw不可用时的回退方案
            self.toggle_mute_fallback()
    
    def toggle_mute_fallback(self):
        if not self.is_muted:
            self.original_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
            self.mute_button.setText("🔊")
            self.is_muted = True
        else:
            self.volume_slider.setValue(self.original_volume)
            self.mute_button.setText("🔇")
            self.is_muted = False
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()
    
    def paintEvent(self, event):
        # 绘制半透明背景
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 180))  # 半透明黑色背景
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRoundedRect(self.rect(), 10, 10)

    def load_settings(self):
        """加载之前保存的设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    # 加载窗口位置
                    self.window_x = settings.get('window_x', None)
                    self.window_y = settings.get('window_y', None)
                    
                    # 加载音量设置
                    saved_volume = settings.get('volume', None)
                    if saved_volume is not None:
                        # 使用保存的音量作为初始音量
                        self.initial_volume = saved_volume
                    else:
                        self.initial_volume = None
            else:
                self.window_x = None
                self.window_y = None
                self.initial_volume = None
        except Exception as e:
            print(f"加载设置时出错: {e}")
            self.window_x = None
            self.window_y = None
            self.initial_volume = None

    def save_settings(self):
        """保存当前设置"""
        try:
            settings = {
                'window_x': self.x(),
                'window_y': self.y(),
                'volume': self.volume_slider.value()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置时出错: {e}")

    def closeEvent(self, event):
        """窗口关闭时保存设置"""
        self.save_settings()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Desktop Volume Control")
    app.setApplicationVersion("1.0")
    
    volume_control = VolumeControl()
    volume_control.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
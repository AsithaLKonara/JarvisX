"""
Floating desktop button for opening chat popup.
"""
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QPushButton, QWidget


class FloatingWidgetButton(QWidget):
    """Draggable floating button."""

    def __init__(self, on_click):
        super().__init__()
        self.on_click = on_click
        self._drag_offset = QPoint()
        self._dragging = False
        self.state = "idle"
        self._setup_ui()
        self._position_bottom_right()

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(72, 72)

        self.button = QPushButton("J", self)
        self.button.setGeometry(6, 6, 60, 60)
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button.clicked.connect(self.on_click)
        self._apply_state_style()

    def set_state(self, state: str):
        """Set orb state: idle/listening/thinking/executing/error."""
        self.state = state
        self._apply_state_style()

    def _apply_state_style(self):
        state_palette = {
            "idle": ("#FFFFFF", "#111827"),
            "listening": ("#60A5FA", "#FFFFFF"),
            "thinking": ("#6366F1", "#FFFFFF"),
            "waiting_approval": ("#F59E0B", "#FFFFFF"),
            "executing": ("#10B981", "#FFFFFF"),
            "error": ("#EF4444", "#FFFFFF"),
        }
        bg, fg = state_palette.get(self.state, state_palette["idle"])
        self.button.setStyleSheet(
            f"""
            QPushButton {{
                border-radius: 30px;
                background-color: {bg};
                color: {fg};
                font-size: 22px;
                font-weight: 700;
                border: 2px solid rgba(255, 255, 255, 0.4);
            }}
            QPushButton:hover {{
                opacity: 0.95;
            }}
            QPushButton:pressed {{
                opacity: 0.85;
            }}
            """
        )

    def _position_bottom_right(self):
        screen = self.screen() or self.windowHandle().screen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        self.move(geometry.right() - self.width() - 24, geometry.bottom() - self.height() - 24)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

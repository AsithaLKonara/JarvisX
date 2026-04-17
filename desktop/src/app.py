"""
Desktop widget application bootstrap.
"""
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from PyQt6.QtGui import QAction, QIcon
from src.backend.chatbot_adapter import ChatbotAdapter
from src.widget_ui.chatbot_popup import ChatbotPopup
from src.widget_ui.widget_button import FloatingWidgetButton


class JarvisApp:
    """Floating widget app with popup chat window."""

    def __init__(self, app: QApplication):
        self.app = app
        self.adapter = ChatbotAdapter()
        self.chat_popup = ChatbotPopup(adapter=self.adapter)
        self.floating_button = FloatingWidgetButton(on_click=self.toggle_chat_popup)
        self.tray_icon = None

        self.setup_system_tray()
        self.chat_popup.state_changed.connect(self.floating_button.set_state)
        self.floating_button.show()

    def setup_system_tray(self):
        """Setup tray icon and quick actions."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setToolTip("JarvisX Widget")
        self.tray_icon.setIcon(QIcon())

        tray_menu = QMenu()

        toggle_action = QAction("Toggle Chat", tray_menu)
        toggle_action.triggered.connect(self.toggle_chat_popup)
        tray_menu.addAction(toggle_action)

        show_button_action = QAction("Show Button", tray_menu)
        show_button_action.triggered.connect(self.floating_button.show)
        tray_menu.addAction(show_button_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", tray_menu)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        """Open popup on tray icon click."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_chat_popup()

    def toggle_chat_popup(self):
        """Show/hide and position popup near floating button."""
        if self.chat_popup.isVisible():
            self.chat_popup.hide()
            return

        self.chat_popup.show()
        self.chat_popup.raise_()
        self.chat_popup.activateWindow()
        self.chat_popup.anchor_near(self.floating_button)

    def quit_app(self):
        """Gracefully shut down desktop widget app."""
        if self.tray_icon:
            self.tray_icon.hide()
        self.chat_popup.close()
        self.floating_button.close()
        self.app.quit()


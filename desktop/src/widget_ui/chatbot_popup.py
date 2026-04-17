"""
Modern JarvisX Chat Widget (Glass + Streaming + Animated UI)
"""

from __future__ import annotations

import html
import re

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from core.contracts import EventType


class ResponseWorker(QThread):
    """Background worker that emits runtime events + streamed chunks."""

    event = pyqtSignal(dict)
    chunk = pyqtSignal(str)
    done = pyqtSignal(str)

    def __init__(self, adapter, text: str):
        super().__init__()
        self.adapter = adapter
        self.text = text

    def run(self):
        output = ""
        for agent_event in self.adapter.stream_response(self.text):
            payload = {
                "type": agent_event.type.value,
                "message": agent_event.message,
                "payload": agent_event.payload,
            }
            self.event.emit(payload)
            if agent_event.type == EventType.RESPONSE_CHUNK:
                output += agent_event.message
                self.chunk.emit(output)
            if agent_event.type == EventType.DONE:
                final = agent_event.message or output
                self.done.emit(final)
                return
        self.done.emit(output)


class ChatbotPopup(QWidget):
    """Glass-style popup chat widget with streaming assistant replies."""
    state_changed = pyqtSignal(str)

    def __init__(self, adapter):
        super().__init__()
        self.adapter = adapter
        self.worker = None
        self.pending_bot_response = ""
        self.current_timeline = []
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("JarvisX")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(440, 640)

        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(18, 18, 22, 0.92);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.08);
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()

        avatar = QLabel("🤖")
        avatar.setStyleSheet("font-size:18px;")

        title = QLabel("JarvisX")
        title.setStyleSheet("color:white; font-weight:700; font-size:15px;")

        status = QLabel("● Online")
        status.setStyleSheet("color:#34D399; font-size:11px;")

        header.addWidget(avatar)
        header.addWidget(title)
        header.addWidget(status)
        header.addStretch()

        close_btn = QPushButton("×")
        close_btn.setFixedSize(28, 28)
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet(
            """
            QPushButton {
                border:none;
                color:white;
                font-size:16px;
                border-radius:6px;
            }
            QPushButton:hover {
                background:rgba(255,255,255,0.1);
            }
            """
        )

        header.addWidget(close_btn)
        root.addLayout(header)

        self.chat_area = QTextBrowser()
        self.chat_area.setOpenExternalLinks(True)
        self.chat_area.setStyleSheet(
            """
            QTextBrowser {
                border:none;
                background:transparent;
                color:white;
                font-size:14px;
            }
            """
        )
        root.addWidget(self.chat_area, stretch=1)

        bottom = QHBoxLayout()

        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Message JarvisX...")
        self.input_line.returnPressed.connect(self.send_message)

        self.input_line.setStyleSheet(
            """
            QLineEdit {
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(255,255,255,0.12);
                border-radius:14px;
                padding:10px;
                color:white;
            }
            QLineEdit:focus {
                border:1px solid #6366F1;
            }
            """
        )

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(42, 42)
        send_btn.clicked.connect(self.send_message)
        send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        send_btn.setStyleSheet(
            """
            QPushButton {
                background:#6366F1;
                color:white;
                border-radius:12px;
                font-size:16px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#7C7FFF;
            }
            """
        )

        bottom.addWidget(self.input_line)
        bottom.addWidget(send_btn)
        root.addLayout(bottom)

        self._append_system("JarvisX ready. Ask me anything.")

    def send_message(self):
        text = self.input_line.text().strip()
        if not text:
            return

        # Avoid concurrent worker overlap in UI.
        if self.worker and self.worker.isRunning():
            return

        self.input_line.clear()
        self._append_user(text)
        self._show_typing()
        self.state_changed.emit("thinking")

        self.worker = ResponseWorker(self.adapter, text)
        self.worker.event.connect(self._handle_runtime_event)
        self.worker.chunk.connect(self._update_stream)
        self.worker.done.connect(self._finish_stream)
        self.worker.start()

    def _update_stream(self, text: str):
        self.pending_bot_response = text
        self._render_chat()

    def _finish_stream(self, text: str):
        self.pending_bot_response = text
        self._hide_typing()
        self._render_chat()
        self._flush_timeline()
        self.state_changed.emit("idle")

    def _append_system(self, msg: str):
        self.chat_area.append(
            f"""
            <div style="text-align:center; color:#9CA3AF; font-size:12px;">
                {html.escape(msg)}
            </div>
            """
        )

    def _append_user(self, msg: str):
        self.chat_area.append(
            f"""
            <div style="text-align:right; margin:8px;">
                <div style="
                    display:inline-block;
                    background:#4F46E5;
                    padding:10px 12px;
                    border-radius:16px;
                    max-width:80%;
                    color:white;">
                    {html.escape(msg)}
                </div>
            </div>
            """
        )
        self._scroll()

    def _show_typing(self):
        self.chat_area.append(
            """
            <div id="typing" style="margin:8px; color:#9CA3AF; font-size:12px;">🤖 typing...</div>
            """
        )
        self._scroll()

    def _handle_runtime_event(self, event: dict):
        event_type = event.get("type", "")
        message = html.escape(event.get("message", ""))
        payload = event.get("payload", {})
        if event_type == EventType.THINKING.value:
            self.current_timeline.append(f"Thinking: {message}")
            self.state_changed.emit("thinking")
        elif event_type == EventType.TOOL_CALL_STARTED.value:
            tool = payload.get("tool", "unknown")
            self.current_timeline.append(f"Tool started: {html.escape(str(tool))}")
            self.state_changed.emit("executing")
        elif event_type == EventType.TOOL_CALL_RESULT.value:
            tool = payload.get("tool", "unknown")
            status = "ok" if not payload.get("error") else "failed"
            self.current_timeline.append(f"Tool result: {html.escape(str(tool))} ({status})")
        elif event_type == EventType.APPROVAL_REQUIRED.value:
            reason = html.escape(payload.get("reason", "Protected action"))
            tool = html.escape(payload.get("tool_name", "action"))
            approval_id = payload.get("approval_id")
            self.chat_area.append(
                f"""
                <div style="text-align:left; margin:8px;">
                    <div style="display:inline-block; background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.4);
                                color:#FCD34D; padding:8px 10px; border-radius:12px; max-width:88%;">
                        ⚠ Approval needed for <b>{tool}</b><br>{reason}<br>
                        <span style="font-size:11px;color:#FDE68A;">Waiting for your decision...</span>
                    </div>
                </div>
                """
            )
            self._scroll()
            approved = self._prompt_approval(tool, reason)
            if approval_id:
                self.adapter.resolve_approval(approval_id, approved)
        elif event_type == EventType.ERROR.value:
            self.current_timeline.append(f"Error: {message}")
            self.state_changed.emit("error")
        elif event_type == EventType.STATE_CHANGED.value:
            state = payload.get("state", "idle")
            self.state_changed.emit(state)

    def _hide_typing(self):
        content = self.chat_area.toHtml()
        content = re.sub(
            r"<div id=\"typing\".*?>.*?</div>",
            "",
            content,
            flags=re.S,
        )
        self.chat_area.setHtml(content)

    def _render_chat(self):
        content = self.chat_area.toHtml()
        content = re.sub(r"<div id=\"streaming-bot\".*?</div>\s*</div>", "", content, flags=re.S)
        bot_html = f"""
        <div id="streaming-bot" style="text-align:left; margin:8px;">
            <div style="
                display:inline-block;
                background:rgba(255,255,255,0.08);
                padding:10px 12px;
                border-radius:16px;
                max-width:80%;
                color:white;">
                🤖 {self._markdown(self.pending_bot_response)}
            </div>
        </div>
        """
        self.chat_area.setHtml(content + bot_html)
        self._scroll()

    def _flush_timeline(self):
        if not self.current_timeline:
            return
        bullet_list = "".join(f"<li>{html.escape(item)}</li>" for item in self.current_timeline[-8:])
        self.chat_area.append(
            f"""
            <div style="text-align:left; margin:8px;">
                <div style="display:inline-block; background:rgba(16,185,129,0.10); border:1px solid rgba(16,185,129,0.35);
                            color:#D1FAE5; padding:8px 10px; border-radius:12px; max-width:88%;">
                    <b>Execution timeline</b>
                    <ul style="margin:6px 0 0 18px; padding:0;">{bullet_list}</ul>
                </div>
            </div>
            """
        )
        self.current_timeline = []
        self._scroll()

    def _prompt_approval(self, tool: str, reason: str) -> bool:
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Approval Required")
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText(f"Allow action: {tool}?")
        dialog.setInformativeText(reason)
        allow_btn = dialog.addButton("Approve", QMessageBox.ButtonRole.AcceptRole)
        deny_btn = dialog.addButton("Deny", QMessageBox.ButtonRole.RejectRole)
        dialog.exec()
        return dialog.clickedButton() == allow_btn and dialog.clickedButton() != deny_btn

    def _scroll(self):
        bar = self.chat_area.verticalScrollBar()
        bar.setValue(bar.maximum())

    def _markdown(self, text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)
        text = re.sub(
            r"(https?://[^\s]+)",
            r"<a href='\1' style='color:#60A5FA;'>\1</a>",
            text,
        )
        return text

    def anchor_near(self, widget: QWidget):
        """Position popup above and near the floating widget button."""
        anchor = widget.frameGeometry()
        x = anchor.right() - self.width() + 14
        y = anchor.top() - self.height() - 12
        self.move(max(12, x), max(12, y))

    def mousePressEvent(self, event):
        self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + diff)
            self.drag_pos = event.globalPosition().toPoint()

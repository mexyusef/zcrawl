"""
Log console widget for displaying application logs.
"""
import logging
from datetime import datetime
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLineEdit, QLabel
)
from PyQt6.QtGui import QTextCursor, QColor


class QTextEditLogger(QObject, logging.Handler):
    """Qt logging handler that emits signals with log messages."""

    log_message = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        """
        Initialize the logger.

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        """
        Emit a log message signal.

        Args:
            record: Logging record
        """
        msg = self.format(record)
        level = record.levelname
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        self.log_message.emit(msg, level, timestamp)


class LogConsoleWidget(QWidget):
    """Widget for displaying application logs."""

    def __init__(self, parent=None):
        """
        Initialize the log console widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set up logging handler
        self.logger_handler = QTextEditLogger()
        self.logger_handler.log_message.connect(self._on_log_message)

        # Set up root logger
        logger = logging.getLogger()
        logger.addHandler(self.logger_handler)
        logger.setLevel(logging.INFO)

        # Stored messages for filtering
        self.log_messages = []

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Controls
        controls_layout = QHBoxLayout()

        # Log level filter
        controls_layout.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_combo.setCurrentText("INFO")
        self.level_combo.currentTextChanged.connect(self._filter_logs)
        controls_layout.addWidget(self.level_combo)

        # Search filter
        controls_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter logs...")
        self.filter_input.textChanged.connect(self._filter_logs)
        controls_layout.addWidget(self.filter_input)

        # Buttons
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        controls_layout.addWidget(self.clear_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_logs)
        controls_layout.addWidget(self.save_button)

        layout.addLayout(controls_layout)

        # Log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.log_view.setFont(self._get_monospace_font())
        layout.addWidget(self.log_view)

    def _get_monospace_font(self):
        """
        Get a monospace font for the log view.

        Returns:
            QFont object with monospace font
        """
        from PyQt6.QtGui import QFont
        font = QFont("Courier New")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)
        return font

    def _on_log_message(self, message: str, level: str, timestamp: str):
        """
        Handle incoming log message.

        Args:
            message: Log message text
            level: Log level (DEBUG, INFO, etc.)
            timestamp: Message timestamp
        """
        # Store message for filtering
        self.log_messages.append({
            'message': message,
            'level': level,
            'timestamp': timestamp
        })

        # Apply filters
        current_level = self.level_combo.currentText()
        current_filter = self.filter_input.text()

        if self._should_show_message(message, level, current_level, current_filter):
            self._append_message(message, level)

    def _should_show_message(self, message: str, level: str, filter_level: str, text_filter: str) -> bool:
        """
        Determine if a message should be shown based on filters.

        Args:
            message: Log message text
            level: Log level (DEBUG, INFO, etc.)
            filter_level: Level filter (DEBUG, INFO, etc.)
            text_filter: Text filter string

        Returns:
            True if message should be shown
        """
        # Check level filter
        level_order = {
            "DEBUG": 0,
            "INFO": 1,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4
        }

        if level_order.get(level, 0) < level_order.get(filter_level, 0):
            return False

        # Check text filter
        if text_filter and text_filter.lower() not in message.lower():
            return False

        return True

    def _append_message(self, message: str, level: str):
        """
        Append a message to the log view with appropriate formatting.

        Args:
            message: Log message text
            level: Log level (DEBUG, INFO, etc.)
        """
        # Set color based on level
        color = self._get_level_color(level)

        # Append with formatting
        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Set text color
        from PyQt6.QtGui import QTextCharFormat
        format = QTextCharFormat()
        format.setForeground(color)

        # Insert text with format
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")

        # Scroll to bottom
        self.log_view.setTextCursor(cursor)
        self.log_view.ensureCursorVisible()

    def _get_level_color(self, level: str) -> QColor:
        """
        Get a color for a log level.

        Args:
            level: Log level (DEBUG, INFO, etc.)

        Returns:
            QColor for the level
        """
        colors = {
            "DEBUG": QColor(100, 100, 100),     # Gray
            "INFO": QColor(0, 0, 0),            # Black
            "WARNING": QColor(255, 165, 0),     # Orange
            "ERROR": QColor(255, 0, 0),         # Red
            "CRITICAL": QColor(128, 0, 128)     # Purple
        }

        return colors.get(level, QColor(0, 0, 0))

    def _filter_logs(self):
        """Apply filters to the log view."""
        # Get current filters
        level_filter = self.level_combo.currentText()
        text_filter = self.filter_input.text()

        # Clear the view
        self.log_view.clear()

        # Re-apply matching messages
        for msg in self.log_messages:
            if self._should_show_message(msg['message'], msg['level'], level_filter, text_filter):
                self._append_message(msg['message'], msg['level'])

    def _save_logs(self):
        """Save logs to a file."""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Logs", "", "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for msg in self.log_messages:
                        f.write(f"{msg['message']}\n")
            except Exception as e:
                # Use direct logging to avoid recursion
                print(f"Error saving logs: {str(e)}")

    def clear(self):
        """Clear the log view and stored messages."""
        self.log_messages.clear()
        self.log_view.clear()

    def log_message(self, message: str, level: str = "INFO"):
        """
        Log a message directly to the console.

        Args:
            message: Message to log
            level: Log level (DEBUG, INFO, etc.)
        """
        log_func = getattr(logging.getLogger(), level.lower(), logging.getLogger().info)
        log_func(message)

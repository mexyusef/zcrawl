"""
Icons module for ZCrawl application.
"""

import os
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt


class IconManager:
    """
    Manages application icons.
    """

    # Icon sizes
    SMALL = QSize(16, 16)
    MEDIUM = QSize(24, 24)
    LARGE = QSize(32, 32)

    @staticmethod
    def get_icon_path(icon_name):
        """Get the path to an icon file."""
        return os.path.join(os.path.dirname(__file__), f"{icon_name}.svg")

    @staticmethod
    def get_icon(icon_name):
        """Get a QIcon for the specified icon name."""
        path = IconManager.get_icon_path(icon_name)
        if os.path.exists(path):
            return QIcon(path)
        else:
            # Return a default icon or placeholder
            return IconManager.create_text_icon(icon_name[0].upper() if icon_name else "?")

    @staticmethod
    def create_text_icon(text, size=SMALL, bg_color="#d1ffd1", text_color="#00008B"):
        """Create a text-based icon when an image is not available."""
        # Create a pixmap
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        # Create a painter and draw the text
        from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QBrush
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background circle
        painter.setPen(QPen(QColor(bg_color)))
        painter.setBrush(QBrush(QColor(bg_color)))
        painter.drawEllipse(0, 0, size.width(), size.height())

        # Draw text
        font = QFont("Arial", size.width() // 2)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(text_color)))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()

        return QIcon(pixmap)

    # Define methods for common icons
    @staticmethod
    def new_icon():
        return IconManager.get_icon("new")

    @staticmethod
    def open_icon():
        return IconManager.get_icon("open")

    @staticmethod
    def save_icon():
        return IconManager.get_icon("save")

    @staticmethod
    def start_icon():
        return IconManager.get_icon("start")

    @staticmethod
    def pause_icon():
        return IconManager.get_icon("pause")

    @staticmethod
    def stop_icon():
        return IconManager.get_icon("stop")

    @staticmethod
    def extract_icon():
        return IconManager.get_icon("extract")

    @staticmethod
    def export_icon():
        return IconManager.get_icon("export")

    @staticmethod
    def settings_icon():
        return IconManager.get_icon("settings")

    @staticmethod
    def single_page_icon():
        return IconManager.get_icon("single_page")

    @staticmethod
    def save_results_icon():
        return IconManager.get_icon("save_results")

"""
Stylesheet manager for ZCrawl application.
"""

from PyQt6.QtWidgets import QApplication


class StylesheetManager:
    """
    Manages application stylesheets and themes.
    """

    @staticmethod
    def apply_theme():
        """Apply the light green background with dark blue text theme."""
        stylesheet = """
        /* Global Application Style */
        QWidget {
            background-color: #e6ffe6;  /* Light green background */
            color: #00008B;             /* Dark blue text */
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        /* Main Window */
        QMainWindow {
            background-color: #e6ffe6;
        }

        /* Toolbar */
        QToolBar {
            background-color: #d1ffd1;
            border-bottom: 1px solid #b3ffb3;
            spacing: 3px;
            padding: 3px;
        }

        QToolButton {
            background-color: #d1ffd1;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 5px;
        }

        QToolButton:hover {
            background-color: #b3ffb3;
            border: 1px solid #99ff99;
        }

        QToolButton:pressed {
            background-color: #99ff99;
        }

        /* Menu Bar */
        QMenuBar {
            background-color: #d1ffd1;
            color: #00008B;
        }

        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }

        QMenuBar::item:selected {
            background-color: #b3ffb3;
        }

        QMenu {
            background-color: #e6ffe6;
            border: 1px solid #b3ffb3;
        }

        QMenu::item {
            padding: 6px 25px 6px 20px;
        }

        QMenu::item:selected {
            background-color: #b3ffb3;
        }

        /* Tab Widget */
        QTabWidget::pane {
            border: 1px solid #b3ffb3;
            background-color: #e6ffe6;
        }

        QTabBar::tab {
            background-color: #d1ffd1;
            color: #00008B;
            border: 1px solid #b3ffb3;
            border-bottom: none;
            padding: 6px 12px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }

        QTabBar::tab:selected {
            background-color: #e6ffe6;
            border-bottom: 1px solid #e6ffe6;
        }

        QTabBar::tab:!selected {
            margin-top: 2px;
        }

        /* Tree Widget */
        QTreeWidget {
            background-color: #f0fff0;
            border: 1px solid #b3ffb3;
        }

        QTreeWidget::item {
            padding: 4px;
        }

        QTreeWidget::item:selected {
            background-color: #b3ffb3;
        }

        /* List Widget */
        QListWidget {
            background-color: #f0fff0;
            border: 1px solid #b3ffb3;
        }

        QListWidget::item {
            padding: 4px;
        }

        QListWidget::item:selected {
            background-color: #b3ffb3;
        }

        /* Buttons */
        QPushButton {
            background-color: #d1ffd1;
            color: #00008B;
            border: 1px solid #b3ffb3;
            border-radius: 4px;
            padding: 6px 12px;
        }

        QPushButton:hover {
            background-color: #b3ffb3;
        }

        QPushButton:pressed {
            background-color: #99ff99;
        }

        /* Text Displays */
        QTextEdit, QTextBrowser {
            background-color: #f0fff0;
            color: #00008B;
            border: 1px solid #b3ffb3;
        }

        /* Status Bar */
        QStatusBar {
            background-color: #d1ffd1;
            color: #00008B;
        }

        /* Frame Headers */
        QFrame {
            background-color: #e6ffe6;
        }

        QFrame#header_frame {
            background-color: #d1ffd1;
        }

        QLabel#header_label {
            color: #00008B;
            font-weight: bold;
            font-size: 14px;
        }

        /* Splitter */
        QSplitter::handle {
            background-color: #b3ffb3;
        }

        /* Form Elements */
        QLineEdit, QComboBox, QSpinBox {
            background-color: #f0fff0;
            border: 1px solid #b3ffb3;
            border-radius: 4px;
            padding: 4px;
            color: #00008B;
        }

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1px solid #99ff99;
        }

        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #e6ffe6;
            width: 12px;
            margin: 12px 0 12px 0;
        }

        QScrollBar::handle:vertical {
            background-color: #b3ffb3;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }

        QScrollBar:horizontal {
            background-color: #e6ffe6;
            height: 12px;
            margin: 0 12px 0 12px;
        }

        QScrollBar::handle:horizontal {
            background-color: #b3ffb3;
            min-width: 20px;
            border-radius: 6px;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: none;
        }

        /* Dock Widgets */
        QDockWidget {
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }

        QDockWidget::title {
            background-color: #d1ffd1;
            padding-left: 5px;
            padding-top: 2px;
            border: 1px solid #b3ffb3;
            border-bottom: none;
        }

        QDockWidget::close-button, QDockWidget::float-button {
            border: none;
            background: transparent;
            padding: 0px;
        }

        QDockWidget::close-button:hover, QDockWidget::float-button:hover {
            background: #b3ffb3;
            border-radius: 2px;
        }

        /* Group Box */
        QGroupBox {
            border: 1px solid #b3ffb3;
            border-radius: 4px;
            margin-top: 10px;
            font-weight: bold;
            color: #00008B;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 3px;
        }

        /* Headers and Help Text */
        QLabel[help="true"] {
            color: #00008B;
            font-size: 11px;
            font-style: italic;
        }
        """

        QApplication.instance().setStyleSheet(stylesheet)

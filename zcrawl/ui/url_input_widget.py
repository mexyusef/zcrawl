"""
URL input widget for entering URLs and configuring crawl options.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox
)
import logging
from colorama import Fore, Style


class URLInputWidget(QWidget):
    """Widget for URL input and crawl options."""

    # Signal emitted when crawl button is clicked with a valid URL
    crawl_requested = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        """
        Initialize the URL input widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # URL input section
        url_layout = QHBoxLayout()

        url_label = QLabel("URL:")
        url_layout.addWidget(url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to crawl (e.g., https://example.com)")
        self.url_input.returnPressed.connect(self._on_crawl_clicked)
        url_layout.addWidget(self.url_input)

        self.crawl_button = QPushButton("Crawl")
        self.crawl_button.clicked.connect(self._on_crawl_clicked)
        self.crawl_button.setAutoDefault(True)
        url_layout.addWidget(self.crawl_button)

        layout.addLayout(url_layout)

        # Options section
        options_layout = QHBoxLayout()

        # Depth selector
        options_layout.addWidget(QLabel("Depth:"))
        self.depth_selector = QComboBox()
        for i in range(1, 11):
            self.depth_selector.addItem(str(i), i)
        self.depth_selector.setCurrentIndex(1)  # Default depth 2
        options_layout.addWidget(self.depth_selector)

        # Same domain only
        self.same_domain_checkbox = QCheckBox("Same Domain Only")
        self.same_domain_checkbox.setChecked(True)
        options_layout.addWidget(self.same_domain_checkbox)

        # Same path only
        self.same_path_checkbox = QCheckBox("Same Path Only")
        self.same_path_checkbox.setChecked(False)
        options_layout.addWidget(self.same_path_checkbox)

        # Respect robots.txt
        self.respect_robots_checkbox = QCheckBox("Respect robots.txt")
        self.respect_robots_checkbox.setChecked(True)
        options_layout.addWidget(self.respect_robots_checkbox)

        # Add options layout
        layout.addLayout(options_layout)

    def _on_crawl_clicked(self):
        """Handle crawl button click or Enter key press in URL input."""
        url = self.url_input.text().strip()

        if not url:
            self.logger.warning(f"{Fore.YELLOW}No URL entered{Style.RESET_ALL}")
            return

        # Add scheme if not present
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.url_input.setText(url)

        # Get options
        options = {
            "depth": self.depth_selector.currentData(),
            "same_domain_only": self.same_domain_checkbox.isChecked(),
            "same_path_only": self.same_path_checkbox.isChecked(),
            "respect_robots_txt": self.respect_robots_checkbox.isChecked()
        }

        self.logger.info(f"{Fore.GREEN}Crawl requested for: {Fore.CYAN}{url}{Style.RESET_ALL} with options: {options}")

        # Emit signal with URL and options
        self.crawl_requested.emit(url, options)

    def get_url(self) -> str:
        """
        Get the current URL.

        Returns:
            Current URL
        """
        return self.url_input.text().strip()

    def get_depth(self) -> int:
        """
        Get the selected depth.

        Returns:
            Selected depth
        """
        return self.depth_selector.currentData()

    def get_options(self) -> dict:
        """
        Get the selected options.

        Returns:
            Dictionary of options
        """
        return {
            "depth": self.depth_selector.currentData(),
            "same_domain_only": self.same_domain_checkbox.isChecked(),
            "same_path_only": self.same_path_checkbox.isChecked(),
            "respect_robots_txt": self.respect_robots_checkbox.isChecked()
        }

    def set_url(self, url: str):
        """
        Set the URL in the input field.

        Args:
            url: URL to set
        """
        self.url_input.setText(url)

    def clear(self):
        """Clear the input field."""
        self.url_input.clear()

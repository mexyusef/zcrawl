"""
Crawl control widget for managing and monitoring crawl operations.
"""
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QGroupBox, QGridLayout,
    QSpinBox, QCheckBox, QTextEdit, QTabWidget
)


class CrawlControlWidget(QWidget):
    """Widget for controlling and monitoring crawl operations."""

    # Signals
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize the crawl control widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QHBoxLayout(self)

        # Left side: Controls and settings
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Button controls
        buttons_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self._on_start_clicked)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.pause_button.setEnabled(False)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.stop_button)

        controls_layout.addLayout(buttons_layout)

        # Progress bar
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        controls_layout.addLayout(progress_layout)

        # Settings
        settings_group = QGroupBox("Crawl Settings")
        settings_layout = QGridLayout(settings_group)

        # Max URLs
        settings_layout.addWidget(QLabel("Max URLs:"), 0, 0)
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(1, 10000)
        self.max_urls_spin.setValue(100)
        settings_layout.addWidget(self.max_urls_spin, 0, 1)

        # Max Depth
        settings_layout.addWidget(QLabel("Max Depth:"), 1, 0)
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 10)
        self.max_depth_spin.setValue(2)
        settings_layout.addWidget(self.max_depth_spin, 1, 1)

        # Delay
        settings_layout.addWidget(QLabel("Delay (seconds):"), 2, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 30)
        self.delay_spin.setValue(1)
        settings_layout.addWidget(self.delay_spin, 2, 1)

        # Checkbox options
        settings_layout.addWidget(QLabel("Options:"), 3, 0)

        options_layout = QVBoxLayout()

        self.same_domain_checkbox = QCheckBox("Same Domain Only")
        self.same_domain_checkbox.setChecked(True)
        options_layout.addWidget(self.same_domain_checkbox)

        self.respect_robots_checkbox = QCheckBox("Respect robots.txt")
        self.respect_robots_checkbox.setChecked(True)
        options_layout.addWidget(self.respect_robots_checkbox)

        self.parallel_checkbox = QCheckBox("Parallel Crawling")
        self.parallel_checkbox.setChecked(True)
        options_layout.addWidget(self.parallel_checkbox)

        settings_layout.addLayout(options_layout, 3, 1)

        controls_layout.addWidget(settings_group)

        # Right side: Statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        # Stats tabs
        stats_tabs = QTabWidget()

        # Summary tab
        summary_widget = QWidget()
        summary_layout = QGridLayout(summary_widget)

        # URLs
        summary_layout.addWidget(QLabel("Total URLs:"), 0, 0)
        self.total_urls_label = QLabel("0")
        summary_layout.addWidget(self.total_urls_label, 0, 1)

        # Crawled
        summary_layout.addWidget(QLabel("Crawled:"), 1, 0)
        self.crawled_urls_label = QLabel("0")
        summary_layout.addWidget(self.crawled_urls_label, 1, 1)

        # Queued
        summary_layout.addWidget(QLabel("Queued:"), 2, 0)
        self.queued_urls_label = QLabel("0")
        summary_layout.addWidget(self.queued_urls_label, 2, 1)

        # Failed
        summary_layout.addWidget(QLabel("Failed:"), 3, 0)
        self.failed_urls_label = QLabel("0")
        summary_layout.addWidget(self.failed_urls_label, 3, 1)

        # Skipped
        summary_layout.addWidget(QLabel("Skipped:"), 4, 0)
        self.skipped_urls_label = QLabel("0")
        summary_layout.addWidget(self.skipped_urls_label, 4, 1)

        # Time elapsed
        summary_layout.addWidget(QLabel("Time Elapsed:"), 5, 0)
        self.time_elapsed_label = QLabel("00:00:00")
        summary_layout.addWidget(self.time_elapsed_label, 5, 1)

        # Rate
        summary_layout.addWidget(QLabel("Crawl Rate:"), 6, 0)
        self.crawl_rate_label = QLabel("0 pages/min")
        summary_layout.addWidget(self.crawl_rate_label, 6, 1)

        # Estimated time remaining
        summary_layout.addWidget(QLabel("Time Remaining:"), 7, 0)
        self.time_remaining_label = QLabel("Unknown")
        summary_layout.addWidget(self.time_remaining_label, 7, 1)

        stats_tabs.addTab(summary_widget, "Summary")

        # Details tab
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        stats_tabs.addTab(self.details_text, "Details")

        stats_layout.addWidget(stats_tabs)

        # Add left and right sides to main layout with a 40/60 split
        main_splitter = QWidget()
        splitter_layout = QHBoxLayout(main_splitter)
        splitter_layout.setContentsMargins(0, 0, 0, 0)
        splitter_layout.addWidget(controls_widget, 4)  # 40%
        splitter_layout.addWidget(stats_widget, 6)     # 60%

        main_layout.addWidget(main_splitter)

    def _on_start_clicked(self):
        """Handle start button click."""
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        # Emit signal
        self.start_requested.emit()

    def _on_pause_clicked(self):
        """Handle pause button click."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

        # Emit signal
        self.pause_requested.emit()

    def _on_stop_clicked(self):
        """Handle stop button click."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Emit signal
        self.stop_requested.emit()

    def update_progress(self, value: int):
        """
        Update the progress bar value.

        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)

    def update_stats(self, stats: dict):
        """
        Update statistics displays.

        Args:
            stats: Dictionary of crawl statistics
        """
        # Update summary labels
        self.total_urls_label.setText(str(stats.get("total_urls", 0)))
        self.crawled_urls_label.setText(str(stats.get("crawled_urls", 0)))
        self.queued_urls_label.setText(str(stats.get("queued_urls", 0)))
        self.failed_urls_label.setText(str(stats.get("failed_urls", 0)))
        self.skipped_urls_label.setText(str(stats.get("skipped_urls", 0)))
        self.time_elapsed_label.setText(stats.get("time_elapsed", "00:00:00"))
        self.crawl_rate_label.setText(stats.get("crawl_rate", "0 pages/min"))
        self.time_remaining_label.setText(stats.get("time_remaining", "Unknown"))

        # Update progress bar if completion percentage is provided
        if "completion_percentage" in stats:
            self.update_progress(stats["completion_percentage"])

        # Update details text if details are provided
        if "details" in stats:
            self.details_text.setText(stats["details"])

    def get_settings(self) -> dict:
        """
        Get the current crawl settings.

        Returns:
            Dictionary of crawl settings
        """
        return {
            "max_urls": self.max_urls_spin.value(),
            "max_depth": self.max_depth_spin.value(),
            "delay": self.delay_spin.value(),
            "same_domain_only": self.same_domain_checkbox.isChecked(),
            "respect_robots_txt": self.respect_robots_checkbox.isChecked(),
            "parallel_crawling": self.parallel_checkbox.isChecked()
        }

    def reset(self):
        """Reset the widget to its initial state."""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.progress_bar.setValue(0)

        self.total_urls_label.setText("0")
        self.crawled_urls_label.setText("0")
        self.queued_urls_label.setText("0")
        self.failed_urls_label.setText("0")
        self.skipped_urls_label.setText("0")
        self.time_elapsed_label.setText("00:00:00")
        self.crawl_rate_label.setText("0 pages/min")
        self.time_remaining_label.setText("Unknown")

        self.details_text.clear()

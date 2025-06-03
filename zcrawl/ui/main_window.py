"""
Main application window for ZCrawl.
"""
import sys
import os
import logging
import time
import threading
import json
import csv
import copy
import html
import traceback
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

from PyQt6.QtCore import Qt, QSize, pyqtSignal, QUrl, QSettings, QTimer
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QDesktopServices
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QDockWidget, QToolBar, QStatusBar,
    QLabel, QLineEdit, QPushButton, QMessageBox, QMenu, QFileDialog,
    QDialog, QGroupBox, QRadioButton, QComboBox, QDialogButtonBox,
    QListWidget, QListWidgetItem, QTextBrowser, QFrame
)
from colorama import Fore, Style

from zcrawl.resources.icons import IconManager
from zcrawl.ui.url_input_widget import URLInputWidget
from zcrawl.ui.crawl_control_widget import CrawlControlWidget
from zcrawl.ui.link_tree_widget import LinkTreeWidget
from zcrawl.ui.content_preview_widget import ContentPreviewWidget
from zcrawl.ui.extraction_designer_widget import ExtractionDesignerWidget
from zcrawl.ui.log_console_widget import LogConsoleWidget
from zcrawl.ui.project_dialog import ProjectDialog
from zcrawl.ui.export_dialog import ExportDialog
from zcrawl.ui.settings_dialog import SettingsDialog
from zcrawl.core.project import Project

from zcrawl.crawlers.http_crawler import HTTPCrawler
from zcrawl.models.url import URL


class MainWindow(QMainWindow):
    """Main application window for ZCrawl."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Set up logger
        self.logger = logging.getLogger(__name__)

        # Initialize crawler
        self.crawler = None

        # Set window properties
        self.setWindowTitle("ZCrawl - Web Crawler and Scraper")
        self.setMinimumSize(1200, 800)

        # Load settings
        self.settings = QSettings("ZCrawl", "ZCrawl")
        self._load_window_settings()

        # Member variables
        self.current_project: Optional[Project] = None

        # Auto-save timer
        self.auto_save_timer = None
        self.auto_save_interval = 300  # Default 5 minutes in seconds
        self.auto_save_enabled = False
        self.save_path = "./results"
        self.save_format = "JSON"
        self.save_screenshots = False
        self.save_with_content = True  # New setting for saving with HTML content

        # Set up UI in the correct order
        self._create_dock_widgets()  # Create docks first so they can be referenced by actions
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_central_widget()
        self._setup_shortcuts()

        # Connect signals
        self._connect_signals()

        # Show welcome message
        self.statusBar().showMessage("Welcome to ZCrawl!")

        self.logger.info(f"{Fore.GREEN}Main window initialized{Style.RESET_ALL}")

    def _create_actions(self) -> None:
        """Create application actions."""
        # File menu actions
        self.action_new_project = QAction(IconManager.new_icon(), "New Project", self)
        self.action_new_project.setStatusTip("Create a new project")
        self.action_new_project.triggered.connect(self._on_new_project)

        self.action_open_project = QAction(IconManager.open_icon(), "Open Project", self)
        self.action_open_project.setStatusTip("Open an existing project")
        self.action_open_project.triggered.connect(self._on_open_project)

        self.action_save_project = QAction(IconManager.save_icon(), "Save Project", self)
        self.action_save_project.setStatusTip("Save the current project")
        self.action_save_project.triggered.connect(self._on_save_project)

        self.action_exit = QAction("Exit", self)
        self.action_exit.setStatusTip("Exit the application")
        self.action_exit.triggered.connect(self.close)

        # Crawl menu actions
        self.action_start_crawl = QAction(IconManager.start_icon(), "Start Crawl", self)
        self.action_start_crawl.setStatusTip("Start crawling")
        self.action_start_crawl.triggered.connect(self._on_start_crawl)

        self.action_single_page_crawl = QAction(IconManager.single_page_icon(), "Crawl Single Page", self)
        self.action_single_page_crawl.setStatusTip("Crawl a single page without following links")
        self.action_single_page_crawl.triggered.connect(self._on_single_page_crawl)

        self.action_pause_crawl = QAction(IconManager.pause_icon(), "Pause Crawl", self)
        self.action_pause_crawl.setStatusTip("Pause crawling")
        self.action_pause_crawl.triggered.connect(self._on_pause_crawl)
        self.action_pause_crawl.setEnabled(False)

        self.action_stop_crawl = QAction(IconManager.stop_icon(), "Stop Crawl", self)
        self.action_stop_crawl.setStatusTip("Stop crawling")
        self.action_stop_crawl.triggered.connect(self._on_stop_crawl)
        self.action_stop_crawl.setEnabled(False)

        # Data menu actions
        self.action_extract_data = QAction(IconManager.extract_icon(), "Extract Data", self)
        self.action_extract_data.setStatusTip("Extract data from current page")
        self.action_extract_data.triggered.connect(self._on_extract_data)

        self.action_export_data = QAction(IconManager.export_icon(), "Export Data", self)
        self.action_export_data.setStatusTip("Export extracted data")
        self.action_export_data.triggered.connect(self._on_export_data)

        self.action_save_results = QAction(IconManager.save_results_icon(), "Save Crawl Results", self)
        self.action_save_results.setStatusTip("Save current crawl results")
        self.action_save_results.triggered.connect(self._on_save_results)
        self.action_save_results.setEnabled(False)

        # View menu actions
        self.action_toggle_log = QAction("Show Log Console", self)
        self.action_toggle_log.setStatusTip("Show/hide log console")
        self.action_toggle_log.setCheckable(True)
        self.action_toggle_log.setChecked(True)

        self.action_toggle_extraction = QAction("Show Extraction Designer", self)
        self.action_toggle_extraction.setStatusTip("Show/hide extraction designer")
        self.action_toggle_extraction.setCheckable(True)
        self.action_toggle_extraction.setChecked(True)

        self.action_toggle_saved_files = QAction("Saved Files Viewer", self)
        self.action_toggle_saved_files.setStatusTip("Toggle saved files viewer visibility")
        self.action_toggle_saved_files.setCheckable(True)
        self.action_toggle_saved_files.setChecked(True)
        self.action_toggle_saved_files.triggered.connect(self.saved_files_dock.setVisible)

        # Help menu actions
        self.action_about = QAction("About", self)
        self.action_about.setStatusTip("Show the application's About box")
        self.action_about.triggered.connect(self._on_about)

        # Settings actions
        self.action_settings = QAction(IconManager.settings_icon(), "Settings", self)
        self.action_settings.setStatusTip("Configure application settings")
        self.action_settings.triggered.connect(self._on_settings)

    def _create_menus(self) -> None:
        """Create application menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.action_new_project)
        file_menu.addAction(self.action_open_project)
        file_menu.addAction(self.action_save_project)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)

        # Crawl menu
        crawl_menu = self.menuBar().addMenu("&Crawl")
        crawl_menu.addAction(self.action_start_crawl)
        crawl_menu.addAction(self.action_single_page_crawl)
        crawl_menu.addSeparator()
        crawl_menu.addAction(self.action_pause_crawl)
        crawl_menu.addAction(self.action_stop_crawl)

        # Data menu
        data_menu = self.menuBar().addMenu("&Data")
        data_menu.addAction(self.action_extract_data)
        data_menu.addAction(self.action_export_data)
        data_menu.addAction(self.action_save_results)

        # View menu
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.action_toggle_log)
        view_menu.addAction(self.action_toggle_extraction)
        view_menu.addAction(self.action_toggle_saved_files)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self.action_about)

        # Tools menu
        tools_menu = self.menuBar().addMenu("&Tools")
        tools_menu.addAction(self.action_settings)

    def _create_toolbars(self) -> None:
        """Create application toolbars."""
        # Main toolbar
        main_toolbar = QToolBar("Main", self)
        main_toolbar.setObjectName("MainToolBar")
        main_toolbar.setMovable(False)
        main_toolbar.setIconSize(QSize(24, 24))

        # Add actions with tooltips instead of text
        main_toolbar.addAction(self.action_new_project)
        main_toolbar.addAction(self.action_open_project)
        main_toolbar.addAction(self.action_save_project)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.action_start_crawl)
        main_toolbar.addAction(self.action_single_page_crawl)
        main_toolbar.addAction(self.action_pause_crawl)
        main_toolbar.addAction(self.action_stop_crawl)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.action_extract_data)
        main_toolbar.addAction(self.action_export_data)
        main_toolbar.addAction(self.action_save_results)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.action_settings)

        self.addToolBar(main_toolbar)

    def _create_status_bar(self) -> None:
        """Create application status bar."""
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Add status indicators
        self.status_urls_label = QLabel("URLs: 0")
        self.status_crawled_label = QLabel("Crawled: 0")
        self.status_queued_label = QLabel("Queued: 0")
        self.status_current_url_label = QLabel("Current: None")

        self.status_bar.addPermanentWidget(self.status_urls_label)
        self.status_bar.addPermanentWidget(self.status_crawled_label)
        self.status_bar.addPermanentWidget(self.status_queued_label)
        self.status_bar.addPermanentWidget(self.status_current_url_label)

    def _create_central_widget(self) -> None:
        """Create the central widget with main layout."""
        # Main widget and layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create splitter for main components
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section: horizontal splitter for tree and content
        top_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: URL input and link tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Header frame for URL input
        url_header_frame = QFrame()
        url_header_frame.setObjectName("header_frame")
        url_header_layout = QVBoxLayout(url_header_frame)
        url_header_layout.setContentsMargins(10, 10, 10, 10)

        url_header_label = QLabel("URL Input")
        url_header_label.setObjectName("header_label")
        url_header_layout.addWidget(url_header_label)

        left_layout.addWidget(url_header_frame)

        # URL input widget
        self.url_input_widget = URLInputWidget()
        self.url_input_widget.crawl_requested.connect(self._on_url_submitted)
        left_layout.addWidget(self.url_input_widget)

        # Header frame for link tree
        tree_header_frame = QFrame()
        tree_header_frame.setObjectName("header_frame")
        tree_header_layout = QVBoxLayout(tree_header_frame)
        tree_header_layout.setContentsMargins(10, 10, 10, 10)

        tree_header_label = QLabel("Link Tree")
        tree_header_label.setObjectName("header_label")
        tree_header_layout.addWidget(tree_header_label)

        left_layout.addWidget(tree_header_frame)

        # Link tree widget
        self.link_tree_widget = LinkTreeWidget()
        self.link_tree_widget.url_selected.connect(self._on_tree_url_selected)
        left_layout.addWidget(self.link_tree_widget, 1)

        top_splitter.addWidget(left_widget)

        # Right side: Content preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Header frame for content preview
        content_header_frame = QFrame()
        content_header_frame.setObjectName("header_frame")
        content_header_layout = QVBoxLayout(content_header_frame)
        content_header_layout.setContentsMargins(10, 10, 10, 10)

        content_header_label = QLabel("Content Preview")
        content_header_label.setObjectName("header_label")
        content_header_layout.addWidget(content_header_label)

        right_layout.addWidget(content_header_frame)

        self.content_preview_widget = ContentPreviewWidget()
        right_layout.addWidget(self.content_preview_widget, 1)

        top_splitter.addWidget(right_widget)

        # Set initial sizes for top splitter
        top_splitter.setSizes([300, 700])

        main_splitter.addWidget(top_splitter)

        # Bottom section: Crawl control panel
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Header frame for crawl control
        control_header_frame = QFrame()
        control_header_frame.setObjectName("header_frame")
        control_header_layout = QVBoxLayout(control_header_frame)
        control_header_layout.setContentsMargins(10, 10, 10, 10)

        control_header_label = QLabel("Crawl Control")
        control_header_label.setObjectName("header_label")
        control_header_layout.addWidget(control_header_label)

        bottom_layout.addWidget(control_header_frame)

        # Help text
        help_label = QLabel(
            "Use the buttons to Start, Pause, or Stop crawling. "
            "The table displays crawled URLs with their status and depth. "
            "Adjust crawl settings like maximum depth and delays on the left side. "
            "Monitor crawl statistics on the right side."
        )
        help_label.setWordWrap(True)
        help_label.setProperty("help", "true")
        help_label.setContentsMargins(10, 0, 10, 10)

        bottom_layout.addWidget(help_label)

        self.crawl_control_widget = CrawlControlWidget()
        self.crawl_control_widget.start_requested.connect(self._on_start_crawl)
        self.crawl_control_widget.pause_requested.connect(self._on_pause_crawl)
        self.crawl_control_widget.stop_requested.connect(self._on_stop_crawl)

        bottom_layout.addWidget(self.crawl_control_widget, 1)

        main_splitter.addWidget(bottom_widget)

        # Set initial sizes for main splitter
        main_splitter.setSizes([600, 200])

        main_layout.addWidget(main_splitter)
        self.setCentralWidget(central_widget)

    def _create_dock_widgets(self) -> None:
        """Create dockable widgets."""
        # Log console dock
        self.log_dock = QDockWidget("Log Console", self)
        self.log_dock.setObjectName("LogDock")
        self.log_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.log_console_widget = LogConsoleWidget()
        self.log_dock.setWidget(self.log_console_widget)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.log_dock)

        # Extraction designer dock
        self.extraction_dock = QDockWidget("Extraction Designer", self)
        self.extraction_dock.setObjectName("ExtractionDock")
        self.extraction_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        self.extraction_designer_widget = ExtractionDesignerWidget()
        self.extraction_dock.setWidget(self.extraction_designer_widget)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.extraction_dock)

        # Saved Files Viewer dock
        self.saved_files_dock = QDockWidget("Saved Files Viewer", self)
        self.saved_files_dock.setObjectName("SavedFilesDock")
        self.saved_files_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.saved_files_widget = QWidget()
        saved_files_layout = QVBoxLayout(self.saved_files_widget)

        # Info section
        info_group = QGroupBox("Save Location Info")
        info_layout = QVBoxLayout(info_group)

        self.save_path_label = QLabel("Current save path: Not set")
        self.save_format_label = QLabel("Current format: Not set")
        self.save_content_label = QLabel("Save with content: No")

        refresh_button = QPushButton("Refresh Files List")
        refresh_button.clicked.connect(self._refresh_saved_files)

        open_folder_button = QPushButton("Open Results Folder")
        open_folder_button.clicked.connect(self._open_results_folder)

        info_layout.addWidget(self.save_path_label)
        info_layout.addWidget(self.save_format_label)
        info_layout.addWidget(self.save_content_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addWidget(open_folder_button)
        info_layout.addLayout(buttons_layout)

        saved_files_layout.addWidget(info_group)

        # Files list
        files_group = QGroupBox("Saved Files")
        files_layout = QVBoxLayout(files_group)

        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self._open_selected_file)

        files_layout.addWidget(self.files_list)
        saved_files_layout.addWidget(files_group)

        # HTML content preview
        html_group = QGroupBox("HTML Content Preview")
        html_layout = QVBoxLayout(html_group)

        self.html_files_list = QListWidget()
        self.html_preview = QTextBrowser()
        self.html_preview.setOpenExternalLinks(True)

        html_splitter = QSplitter(Qt.Orientation.Vertical)
        html_splitter.addWidget(self.html_files_list)
        html_splitter.addWidget(self.html_preview)
        html_splitter.setSizes([100, 300])

        self.html_files_list.itemClicked.connect(self._preview_html_file)

        html_layout.addWidget(html_splitter)
        saved_files_layout.addWidget(html_group)

        self.saved_files_dock.setWidget(self.saved_files_widget)

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.saved_files_dock)

        # Update save info now
        self._update_save_info()

        # Set up timer to refresh files list periodically
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_saved_files)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        self.action_new_project.setShortcut(QKeySequence.StandardKey.New)
        self.action_open_project.setShortcut(QKeySequence.StandardKey.Open)
        self.action_save_project.setShortcut(QKeySequence.StandardKey.Save)
        self.action_exit.setShortcut(QKeySequence("Ctrl+Q"))

        self.action_start_crawl.setShortcut(QKeySequence("Ctrl+R"))
        self.action_pause_crawl.setShortcut(QKeySequence("Ctrl+P"))
        self.action_stop_crawl.setShortcut(QKeySequence("Ctrl+T"))

        self.action_extract_data.setShortcut(QKeySequence("Ctrl+E"))

        self.action_toggle_log.setShortcut(QKeySequence("Ctrl+L"))
        self.action_toggle_extraction.setShortcut(QKeySequence("Ctrl+D"))

    def _connect_signals(self):
        """Connect widget signals."""
        # URL input widget
        self.url_input_widget.crawl_requested.connect(self._on_url_submitted)

        # Link tree widget
        self.link_tree_widget.url_selected.connect(self._on_tree_url_selected)

        # Crawl control widget
        self.crawl_control_widget.start_requested.connect(self._on_start_crawl)
        self.crawl_control_widget.pause_requested.connect(self._on_pause_crawl)
        self.crawl_control_widget.stop_requested.connect(self._on_stop_crawl)

        # Connect dock toggles
        self.action_toggle_log.triggered.connect(self.log_dock.setVisible)
        self.action_toggle_extraction.triggered.connect(self.extraction_dock.setVisible)
        self.action_toggle_saved_files.triggered.connect(self.saved_files_dock.setVisible)

    def _on_url_submitted(self, url: str, options: dict):
        """
        Handle URL submission.

        Args:
            url: URL to crawl
            options: Crawling options
        """
        self.logger.info(f"{Fore.GREEN}URL submitted: {Fore.CYAN}{url}{Style.RESET_ALL}")
        self.logger.info(f"{Fore.GREEN}Options: {options}{Style.RESET_ALL}")

        # Start crawling
        self._on_start_crawl(url, options)

    def _on_tree_url_selected(self, url: str) -> None:
        """
        Handle URL selection in the link tree.

        Args:
            url: Selected URL
        """
        self.statusBar().showMessage(f"Selected URL: {url}")

        # Load the URL in the content preview
        self.content_preview_widget.load_url(url)

    def _on_start_crawl(self, url: Optional[str] = None, options: Optional[dict] = None):
        """
        Handle start crawl action.

        Args:
            url: URL to crawl (optional, uses URL input if not provided)
            options: Crawling options (optional, uses UI settings if not provided)
        """
        # Get URL from input if not provided
        if not url:
            url = self.url_input_widget.get_url()
            if not url:
                self.logger.warning(f"{Fore.YELLOW}No URL specified for crawling{Style.RESET_ALL}")
                QMessageBox.warning(self, "Crawl Error", "Please enter a URL to crawl.")
                return

        # Get options if not provided
        if not options:
            options = self.url_input_widget.get_options()

        # Log the start
        self.logger.info(f"{Fore.GREEN}Starting crawl: {Fore.CYAN}{url}{Style.RESET_ALL}")
        self.logger.info(f"{Fore.GREEN}Crawl options: {options}{Style.RESET_ALL}")

        # Update UI
        self.action_start_crawl.setEnabled(False)
        self.action_pause_crawl.setEnabled(True)
        self.action_stop_crawl.setEnabled(True)
        self.action_save_results.setEnabled(True)

        # Clear existing data
        self.link_tree_widget.clear()

        # Initialize crawler if needed
        if not self.crawler:
            self.crawler = HTTPCrawler(
                max_depth=options.get("depth", 2),
                same_domain_only=options.get("same_domain_only", True),
                respect_robots_txt=options.get("respect_robots_txt", True)
            )

        # Start crawler
        self.crawler.start(url)

        # Start auto-save timer if enabled
        if self.auto_save_enabled:
            self._manage_auto_save_timer()

        # Update status bar
        self.status_current_url_label.setText("Crawling...")

    def _on_pause_crawl(self) -> None:
        """Handle pausing a crawl."""
        self.statusBar().showMessage("Crawl paused.")

        # Update UI state
        self.action_start_crawl.setEnabled(True)
        self.action_pause_crawl.setEnabled(False)

        # Log message
        self.log_console_widget.log_message("Crawl paused")

    def _on_stop_crawl(self) -> None:
        """Handle stopping a crawl."""
        self.statusBar().showMessage("Crawl stopped.")

        # Update UI state
        self.action_start_crawl.setEnabled(True)
        self.action_pause_crawl.setEnabled(False)
        self.action_stop_crawl.setEnabled(False)

        # Stop crawler
        if self.crawler:
            self.crawler.stop()

            # Stop auto-save timer
            if self.auto_save_timer:
                self.auto_save_timer.cancel()
                self.auto_save_timer = None

        # Log message
        self.log_console_widget.log_message("Crawl stopped")

    def _on_extract_data(self) -> None:
        """Handle extracting data from the current page."""
        # This would be connected to actual extraction logic
        self.statusBar().showMessage("Data extraction initiated.")

        # Log message
        self.log_console_widget.log_message("Data extraction initiated")

    def _on_export_data(self) -> None:
        """Handle exporting extracted data."""
        # This would be connected to actual export logic
        self.statusBar().showMessage("Data export initiated.")

        # Log message
        self.log_console_widget.log_message("Data export initiated")

    def _on_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About ZCrawl",
            "ZCrawl - Advanced Web Crawling & Scraping Desktop Application\n\n"
            "Version 0.0.1\n\n"
            "A comprehensive tool for crawling websites and extracting data."
        )

    def _on_settings(self):
        """Handle settings action."""
        self.logger.info(f"{Fore.GREEN}Settings requested{Style.RESET_ALL}")

        dialog = SettingsDialog(self)
        if dialog.exec():
            self.logger.info(f"{Fore.GREEN}Settings updated{Style.RESET_ALL}")

            # Apply settings
            save_settings = dialog.get_save_results_settings()
            self.auto_save_enabled = save_settings.get('auto_save', False)
            self.auto_save_interval = save_settings.get('save_interval', 5) * 60  # Convert minutes to seconds
            self.save_path = save_settings.get('save_location', './results')
            self.save_format = save_settings.get('save_format', 'JSON')
            self.save_screenshots = save_settings.get('save_screenshots', False)
            self.save_with_content = save_settings.get('save_with_content', True)

            # Create save directory if it doesn't exist
            if self.auto_save_enabled and not os.path.exists(self.save_path):
                try:
                    os.makedirs(self.save_path)
                    self.logger.info(f"{Fore.GREEN}Created save directory: {self.save_path}{Style.RESET_ALL}")
                except Exception as e:
                    self.logger.error(f"{Fore.RED}Error creating save directory: {str(e)}{Style.RESET_ALL}")

            # Start or stop auto-save timer
            self._manage_auto_save_timer()

            # Update save info
            self._update_save_info()

    def _load_window_settings(self):
        """Load window settings."""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))

    def _save_window_settings(self):
        """Save window settings."""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Save window settings
        self._save_window_settings()

        # Stop crawler if running
        if self.crawler:
            self.crawler.stop()

        event.accept()

    def _on_new_project(self):
        """Handle creating a new project."""
        self.logger.info(f"{Fore.GREEN}New project requested{Style.RESET_ALL}")

        dialog = ProjectDialog(self, "New Project")
        if dialog.exec():
            project_name = dialog.get_project_name()
            self.logger.info(f"{Fore.GREEN}New project created: {Fore.CYAN}{project_name}{Style.RESET_ALL}")

            # Clear existing data
            self.link_tree_widget.clear()
            self.content_preview_widget.clear()
            self.url_input_widget.clear()

            # Update window title
            self.setWindowTitle(f"ZCrawl - {project_name}")

            # Log message
            self.log_console_widget.log_message(f"New project created: {project_name}")

    def _on_open_project(self):
        """Handle opening an existing project."""
        self.logger.info(f"{Fore.GREEN}Open project requested{Style.RESET_ALL}")

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "ZCrawl Projects (*.zcrawl);;All Files (*)"
        )

        if file_path:
            self.logger.info(f"{Fore.GREEN}Opening project: {Fore.CYAN}{file_path}{Style.RESET_ALL}")

            # Project loading logic would go here
            # For now, just update status and log
            project_name = os.path.basename(file_path).replace(".zcrawl", "")
            self.setWindowTitle(f"ZCrawl - {project_name}")
            self.statusBar().showMessage(f"Opened project: {project_name}")
            self.log_console_widget.log_message(f"Opened project: {file_path}")

    def _on_save_project(self):
        """Handle saving the current project."""
        self.logger.info(f"{Fore.GREEN}Save project requested{Style.RESET_ALL}")

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project", "", "ZCrawl Projects (*.zcrawl);;All Files (*)"
        )

        if file_path:
            self.logger.info(f"{Fore.GREEN}Saving project to: {Fore.CYAN}{file_path}{Style.RESET_ALL}")

            # Project saving logic would go here
            # For now, just update status and log
            self.statusBar().showMessage(f"Project saved to: {file_path}")
            self.log_console_widget.log_message(f"Project saved to: {file_path}")

    def _manage_auto_save_timer(self):
        """Start or stop the auto-save timer based on settings."""
        # Stop existing timer if any
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None

        # Start new timer if enabled
        if self.auto_save_enabled and self.crawler and self.crawler.running:
            self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save_results)
            self.auto_save_timer.daemon = True
            self.auto_save_timer.start()
            self.logger.info(f"{Fore.GREEN}Auto-save timer started ({self.auto_save_interval / 60} minutes){Style.RESET_ALL}")

    def _auto_save_results(self):
        """Automatically save crawl results based on settings."""
        if not self.crawler or not self.crawler.running:
            return

        try:
            # Check if there are any pages to save
            if not self.crawler.pages:
                self.logger.warning(f"{Fore.YELLOW}No pages to save yet, skipping auto-save{Style.RESET_ALL}")
                # Schedule next save anyway
                self._manage_auto_save_timer()
                return

            # Generate timestamp for filename
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename_base = f"zcrawl_results_{timestamp}"

            # Create a path with absolute path
            save_path = os.path.abspath(self.save_path)
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)

            filepath = os.path.join(save_path, f"{filename_base}.{self.save_format.lower()}")

            self.logger.info(f"{Fore.GREEN}Auto-saving to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")

            # If not saving with content, create temporary modified pages
            if not self.save_with_content:
                # Create temporary copies of pages without HTML content
                temp_pages = {}
                for url, page in self.crawler.pages.items():
                    # Create a shallow copy of the page
                    temp_page = copy.copy(page)
                    # Remove HTML content to save space
                    temp_page.html_content = None
                    temp_pages[url] = temp_page

                # Store original pages
                original_pages = self.crawler.pages

                # Replace with modified pages
                self.crawler.pages = temp_pages

                # Save based on format
                if self.save_format == "JSON":
                    self._save_results_json(filepath)
                elif self.save_format == "CSV":
                    self._save_results_csv(filepath)
                elif self.save_format == "HTML":
                    self._save_results_html(filepath)
                elif self.save_format == "XML":
                    self._save_results_xml(filepath)

                # Restore original pages
                self.crawler.pages = original_pages
            else:
                # Save with full content
                if self.save_format == "JSON":
                    self._save_results_json(filepath)
                elif self.save_format == "CSV":
                    self._save_results_csv(filepath)
                elif self.save_format == "HTML":
                    self._save_results_html(filepath)
                elif self.save_format == "XML":
                    self._save_results_xml(filepath)

            # Log success
            self.logger.info(f"{Fore.GREEN}Auto-saved results to {filepath}{Style.RESET_ALL}")
            self.log_console_widget.log_message(f"Auto-saved results to {filepath}")

            # Schedule next save
            self._manage_auto_save_timer()
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error auto-saving results: {str(e)}{Style.RESET_ALL}")
            self.log_console_widget.log_message(f"Error auto-saving results: {str(e)}")
            traceback.print_exc()

            # Try again later anyway
            self._manage_auto_save_timer()

    def _save_results_json(self, filepath):
        """Save crawl results as JSON."""
        # Convert to absolute path and normalize
        filepath = os.path.abspath(filepath)

        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "crawled_urls": list(self.crawler.visited_urls),
            "pages": {}
        }

        # Add page data
        for url, page in self.crawler.pages.items():
            data["pages"][url] = {
                "title": page.title,
                "status_code": page.status_code,
                "links": page.links,
                "images": page.images,
                "depth": self.crawler.url_objects[url].depth if url in self.crawler.url_objects else 0,
                "html_content": page.html_content,
                "text_content": page.text_content,
                "meta_tags": page.meta_tags,
                "content_type": page.content_type,
                "fetched_at": page.fetched_at.isoformat() if hasattr(page, 'fetched_at') else None
            }

        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        self.logger.info(f"{Fore.GREEN}Saving to directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
        os.makedirs(directory, exist_ok=True)

        self.logger.info(f"{Fore.GREEN}Saving file to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Log file size
        file_size = os.path.getsize(filepath)
        self.logger.info(f"{Fore.GREEN}File saved: {Fore.CYAN}{filepath}{Fore.GREEN} ({file_size} bytes){Style.RESET_ALL}")

        # Create individual HTML files with content
        if self.save_with_content and file_size > 0:
            html_dir = os.path.join(directory, "html_content")
            self.logger.info(f"{Fore.GREEN}Creating HTML directory: {Fore.CYAN}{html_dir}{Style.RESET_ALL}")
            os.makedirs(html_dir, exist_ok=True)

            html_files_saved = 0
            for url, page in self.crawler.pages.items():
                if page.html_content:
                    # Create a valid filename from the URL
                    safe_filename = "".join([c if c.isalnum() else "_" for c in url])
                    safe_filename = safe_filename[-100:] if len(safe_filename) > 100 else safe_filename
                    html_path = os.path.join(html_dir, f"{safe_filename}.html")

                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(page.html_content)

                    html_files_saved += 1

            self.logger.info(f"{Fore.GREEN}HTML content saved: {Fore.CYAN}{html_files_saved}{Fore.GREEN} files in {html_dir}{Style.RESET_ALL}")

            # Create an index.html file for easier browsing
            index_path = os.path.join(html_dir, "index.html")
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>ZCrawl Results - {time.strftime("%Y-%m-%d %H:%M:%S")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>ZCrawl Results - {time.strftime("%Y-%m-%d %H:%M:%S")}</h1>
    <p>Total pages: {len(self.crawler.pages)}</p>
    <table>
        <tr>
            <th>URL</th>
            <th>Title</th>
            <th>Status</th>
            <th>HTML File</th>
        </tr>
""")

                for url, page in self.crawler.pages.items():
                    safe_filename = "".join([c if c.isalnum() else "_" for c in url])
                    safe_filename = safe_filename[-100:] if len(safe_filename) > 100 else safe_filename
                    html_filename = f"{safe_filename}.html"

                    f.write(f"""        <tr>
            <td><a href="{url}" target="_blank">{url}</a></td>
            <td>{page.title or 'No title'}</td>
            <td>{page.status_code or 'Unknown'}</td>
            <td><a href="{html_filename}">{html_filename}</a></td>
        </tr>
""")

                f.write("""    </table>
</body>
</html>""")

            self.logger.info(f"{Fore.GREEN}Created HTML index: {Fore.CYAN}{index_path}{Style.RESET_ALL}")

        # Update the saved files view
        self._update_save_info()

    def _save_results_csv(self, filepath):
        """Save crawl results as CSV."""
        # Convert to absolute path and normalize
        filepath = os.path.abspath(filepath)

        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        self.logger.info(f"{Fore.GREEN}Saving CSV to directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
        os.makedirs(directory, exist_ok=True)

        self.logger.info(f"{Fore.GREEN}Saving CSV file to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Status', 'Depth', 'Links Count', 'Images Count'])

            for url, page in self.crawler.pages.items():
                writer.writerow([
                    url,
                    page.title,
                    page.status_code,
                    self.crawler.url_objects[url].depth if url in self.crawler.url_objects else 0,
                    len(page.links),
                    len(page.images)
                ])

        # Log file size
        file_size = os.path.getsize(filepath)
        self.logger.info(f"{Fore.GREEN}CSV file saved: {Fore.CYAN}{filepath}{Fore.GREEN} ({file_size} bytes){Style.RESET_ALL}")

    def _save_results_html(self, filepath):
        """Save crawl results as HTML."""
        # Convert to absolute path and normalize
        filepath = os.path.abspath(filepath)

        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        self.logger.info(f"{Fore.GREEN}Saving HTML to directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
        os.makedirs(directory, exist_ok=True)

        self.logger.info(f"{Fore.GREEN}Saving HTML file to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>ZCrawl Results - {time.strftime("%Y-%m-%d %H:%M:%S")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>ZCrawl Results - {time.strftime("%Y-%m-%d %H:%M:%S")}</h1>
    <table>
        <tr>
            <th>URL</th>
            <th>Title</th>
            <th>Status</th>
            <th>Depth</th>
            <th>Links</th>
            <th>Images</th>
        </tr>
"""

        # Add table rows
        for url, page in self.crawler.pages.items():
            depth = self.crawler.url_objects[url].depth if url in self.crawler.url_objects else 0
            html += f"""
        <tr>
            <td><a href="{url}" target="_blank">{url}</a></td>
            <td>{page.title}</td>
            <td>{page.status_code}</td>
            <td>{depth}</td>
            <td>{len(page.links)}</td>
            <td>{len(page.images)}</td>
        </tr>"""

        html += """
    </table>
</body>
</html>"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        # Log file size
        file_size = os.path.getsize(filepath)
        self.logger.info(f"{Fore.GREEN}HTML file saved: {Fore.CYAN}{filepath}{Fore.GREEN} ({file_size} bytes){Style.RESET_ALL}")

    def _save_results_xml(self, filepath):
        """Save crawl results as XML."""
        # Convert to absolute path and normalize
        filepath = os.path.abspath(filepath)

        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        self.logger.info(f"{Fore.GREEN}Saving XML to directory: {Fore.CYAN}{directory}{Style.RESET_ALL}")
        os.makedirs(directory, exist_ok=True)

        self.logger.info(f"{Fore.GREEN}Saving XML file to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<crawl_results timestamp="{time.strftime("%Y-%m-%d %H:%M:%S")}">
"""

        for url, page in self.crawler.pages.items():
            depth = self.crawler.url_objects[url].depth if url in self.crawler.url_objects else 0
            xml += f"""    <page>
        <url>{url}</url>
        <title>{page.title}</title>
        <status_code>{page.status_code}</status_code>
        <depth>{depth}</depth>
        <links_count>{len(page.links)}</links_count>
        <images_count>{len(page.images)}</images_count>
    </page>
"""

        xml += "</crawl_results>"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml)

        # Log file size
        file_size = os.path.getsize(filepath)
        self.logger.info(f"{Fore.GREEN}XML file saved: {Fore.CYAN}{filepath}{Fore.GREEN} ({file_size} bytes){Style.RESET_ALL}")

    def _on_save_results(self) -> None:
        """Handle manually saving crawl results."""
        if not self.crawler or not self.crawler.pages:
            QMessageBox.warning(self, "No Results", "There are no crawl results to save.")
            return

        try:
            # Create dialog for save options
            save_dialog = QDialog(self)
            save_dialog.setWindowTitle("Save Crawl Results")
            save_dialog.setMinimumWidth(400)

            dialog_layout = QVBoxLayout(save_dialog)

            # Save content options
            content_group = QGroupBox("Content Options")
            content_layout = QVBoxLayout(content_group)

            save_metadata_only = QRadioButton("Save metadata only (URLs, titles, status)")
            save_metadata_only.setChecked(False)

            save_with_content = QRadioButton("Save with full HTML content (larger files)")
            save_with_content.setChecked(True)

            content_layout.addWidget(save_metadata_only)
            content_layout.addWidget(save_with_content)

            dialog_layout.addWidget(content_group)

            # Format options
            format_group = QGroupBox("Format")
            format_layout = QVBoxLayout(format_group)

            formats = [
                ("JSON Format (*.json)", "JSON"),
                ("CSV Format (*.csv)", "CSV"),
                ("HTML Format (*.html)", "HTML"),
                ("XML Format (*.xml)", "XML")
            ]

            format_combo = QComboBox()
            for label, _ in formats:
                format_combo.addItem(label)

            format_layout.addWidget(format_combo)
            dialog_layout.addWidget(format_group)

            # Add filename input
            filename_layout = QHBoxLayout()
            filename_layout.addWidget(QLabel("Filename:"))

            default_filename = f"zcrawl_results_{time.strftime('%Y%m%d_%H%M%S')}"
            filename_input = QLineEdit(default_filename)
            filename_layout.addWidget(filename_input)

            dialog_layout.addLayout(filename_layout)

            # Add save location
            location_layout = QHBoxLayout()
            location_layout.addWidget(QLabel("Save location:"))

            # Use absolute path for results folder in workspace
            default_results_path = os.path.abspath(os.path.join(os.getcwd(), "results"))
            location_input = QLineEdit(default_results_path)
            browse_button = QPushButton("Browse...")

            def browse_save_location():
                directory = QFileDialog.getExistingDirectory(
                    save_dialog, "Select Save Directory", location_input.text()
                )
                if directory:
                    location_input.setText(directory)

            browse_button.clicked.connect(browse_save_location)

            location_layout.addWidget(location_input)
            location_layout.addWidget(browse_button)

            dialog_layout.addLayout(location_layout)

            # Buttons
            button_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
            )
            button_box.accepted.connect(save_dialog.accept)
            button_box.rejected.connect(save_dialog.reject)

            dialog_layout.addWidget(button_box)

            # Show dialog
            if save_dialog.exec() != QDialog.DialogCode.Accepted:
                return

            # Get values
            save_with_content_enabled = save_with_content.isChecked()
            selected_format = formats[format_combo.currentIndex()][1]
            filename = filename_input.text()
            save_location = location_input.text()

            # Ensure directory exists with absolute path
            save_location = os.path.abspath(save_location)
            self.logger.info(f"{Fore.GREEN}Creating directory: {Fore.CYAN}{save_location}{Style.RESET_ALL}")
            os.makedirs(save_location, exist_ok=True)

            # Set up file path with extension
            extension = selected_format.lower()
            filepath = os.path.join(save_location, f"{filename}.{extension}")
            self.logger.info(f"{Fore.GREEN}Full filepath: {Fore.CYAN}{filepath}{Style.RESET_ALL}")

            # Save with content (create a special save method that removes HTML content if not needed)
            if not save_with_content_enabled:
                # Create temporary copies of pages without HTML content
                temp_pages = {}
                for url, page in self.crawler.pages.items():
                    # Create a shallow copy of the page
                    temp_page = copy.copy(page)
                    # Remove HTML content to save space
                    temp_page.html_content = None
                    temp_pages[url] = temp_page

                # Store original pages
                original_pages = self.crawler.pages

                # Replace with modified pages
                self.crawler.pages = temp_pages

                # Save with the appropriate format
                if selected_format == "JSON":
                    self._save_results_json(filepath)
                elif selected_format == "CSV":
                    self._save_results_csv(filepath)
                elif selected_format == "HTML":
                    self._save_results_html(filepath)
                elif selected_format == "XML":
                    self._save_results_xml(filepath)

                # Restore original pages
                self.crawler.pages = original_pages
            else:
                # Save with full content
                if selected_format == "JSON":
                    self._save_results_json(filepath)
                elif selected_format == "CSV":
                    self._save_results_csv(filepath)
                elif selected_format == "HTML":
                    self._save_results_html(filepath)
                elif selected_format == "XML":
                    self._save_results_xml(filepath)

            # Check if file was saved
            if os.path.exists(filepath):
                filesize = os.path.getsize(filepath)
                self.logger.info(f"{Fore.GREEN}File saved: {Fore.CYAN}{filepath}{Fore.GREEN} ({filesize} bytes){Style.RESET_ALL}")
                if filesize == 0:
                    QMessageBox.warning(self, "Empty File", f"The file was saved but contains no data (0 bytes): {filepath}")
                    return

                # Open the containing folder
                if QMessageBox.question(
                    self,
                    "File Saved",
                    f"Results saved to: {filepath}\n\nDo you want to open the containing folder?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                ) == QMessageBox.StandardButton.Yes:
                    if sys.platform == 'win32':
                        os.startfile(os.path.dirname(filepath))
                    elif sys.platform == 'darwin':  # macOS
                        subprocess.Popen(['open', os.path.dirname(filepath)])
                    else:  # Linux variants
                        subprocess.Popen(['xdg-open', os.path.dirname(filepath)])
            else:
                QMessageBox.warning(self, "Save Error", f"File could not be created: {filepath}")
                return

            # Log success
            self.statusBar().showMessage(f"Results saved to: {filepath}")
            self.log_console_widget.log_message(f"Results saved to: {filepath}")
            self.logger.info(f"{Fore.GREEN}Results saved to: {Fore.CYAN}{filepath}{Style.RESET_ALL}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving results: {str(e)}")
            self.logger.error(f"{Fore.RED}Error saving results: {str(e)}{Style.RESET_ALL}")
            traceback.print_exc()

    def _on_single_page_crawl(self):
        """Handle crawling a single page without following links."""
        # Get URL from input
        url = self.url_input_widget.get_url()
        if not url:
            self.logger.warning(f"{Fore.YELLOW}No URL specified for crawling{Style.RESET_ALL}")
            QMessageBox.warning(self, "Crawl Error", "Please enter a URL to crawl.")
            return

        self.logger.info(f"{Fore.GREEN}Starting single page crawl: {Fore.CYAN}{url}{Style.RESET_ALL}")

        # Initialize crawler if needed
        if not self.crawler:
            self.crawler = HTTPCrawler(
                max_depth=0,  # Don't follow any links
                same_domain_only=True,
                respect_robots_txt=True
            )
        else:
            # Configure existing crawler to only get one page
            self.crawler.max_depth = 0
            # Clear previous pages and queue
            self.crawler.pages.clear()
            self.crawler.visited_urls.clear()
            with self.crawler.url_queue.mutex:
                self.crawler.url_queue.queue.clear()

        # Update UI
        self.action_start_crawl.setEnabled(False)
        self.action_single_page_crawl.setEnabled(False)
        self.action_stop_crawl.setEnabled(True)
        self.action_save_results.setEnabled(True)

        # Clear existing data
        self.link_tree_widget.clear()

        # Start crawler
        self.crawler.start(url)

        # Update status bar
        self.status_current_url_label.setText(f"Crawling: {url}")
        self.log_console_widget.log_message(f"Single page crawl started: {url}")

        # Ask if user wants to save the result immediately
        def ask_to_save_result():
            # Wait a bit for the page to be crawled
            time.sleep(2)
            if self.crawler and self.crawler.pages and not self.crawler.running:
                # Check again in case crawl failed
                if not self.crawler.pages:
                    self.logger.warning(f"{Fore.YELLOW}No pages were crawled{Style.RESET_ALL}")
                    self.log_console_widget.log_message("No pages were crawled")
                    return

                reply = QMessageBox.question(
                    self,
                    "Save Result",
                    "Single page crawl completed. Do you want to save the result?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._on_save_results()

        # Run in a separate thread to avoid blocking UI
        save_thread = threading.Thread(target=ask_to_save_result)
        save_thread.daemon = True
        save_thread.start()

    def _update_save_info(self):
        """Update the save information display."""
        # Update labels
        self.save_path_label.setText(f"Current save path: {os.path.abspath(self.save_path)}")
        self.save_format_label.setText(f"Current format: {self.save_format}")
        self.save_content_label.setText(f"Save with content: {'Yes' if self.save_with_content else 'No'}")

        # Refresh the files list
        self._refresh_saved_files()

    def _refresh_saved_files(self):
        """Refresh the list of saved files."""
        self.files_list.clear()
        self.html_files_list.clear()

        try:
            # Get the absolute path
            abs_path = os.path.abspath(self.save_path)

            # Check if path exists
            if not os.path.exists(abs_path):
                self.files_list.addItem("Save path does not exist: " + abs_path)
                return

            # Add files to the list
            for root, dirs, files in os.walk(abs_path):
                for file in files:
                    if file.lower().endswith(('.json', '.csv', '.html', '.xml')):
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, abs_path)
                        item = QListWidgetItem(rel_path)
                        item.setToolTip(full_path)
                        self.files_list.addItem(item)

            # Check for HTML content folder
            html_content_dir = os.path.join(abs_path, "html_content")
            if os.path.exists(html_content_dir):
                for file in os.listdir(html_content_dir):
                    if file.lower().endswith('.html'):
                        full_path = os.path.join(html_content_dir, file)
                        item = QListWidgetItem(file)
                        item.setToolTip(full_path)
                        self.html_files_list.addItem(item)

            # Also check for any HTML content folders in the workspace root
            workspace_root = os.getcwd()
            for root, dirs, files in os.walk(workspace_root):
                if os.path.basename(root) == "html_content":
                    for file in files:
                        if file.lower().endswith('.html'):
                            full_path = os.path.join(root, file)
                            item = QListWidgetItem(f"{os.path.basename(os.path.dirname(root))}/{file}")
                            item.setToolTip(full_path)
                            self.html_files_list.addItem(item)

            # Check if we found any files
            if self.files_list.count() == 0:
                self.files_list.addItem("No saved files found in: " + abs_path)

            # Add a special item if we see result files in the workspace root
            json_files_in_root = [f for f in os.listdir(workspace_root) if f.startswith("zcrawl_results_") and f.endswith(".json")]
            if json_files_in_root:
                self.files_list.addItem("---------------")
                self.files_list.addItem("Files in workspace root:")
                for file in json_files_in_root:
                    item = QListWidgetItem(file + " (in root)")
                    item.setToolTip(os.path.join(workspace_root, file))
                    self.files_list.addItem(item)

        except Exception as e:
            self.files_list.addItem(f"Error listing files: {str(e)}")
            traceback.print_exc()

    def _open_selected_file(self, item):
        """Open the selected file."""
        filepath = item.toolTip()
        try:
            if os.path.exists(filepath):
                if sys.platform == 'win32':
                    os.startfile(filepath)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.Popen(['open', filepath])
                else:  # Linux variants
                    subprocess.Popen(['xdg-open', filepath])
            else:
                QMessageBox.warning(self, "File Not Found", f"Cannot find file: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening file: {str(e)}")

    def _preview_html_file(self, item):
        """Preview the selected HTML file."""
        filepath = item.toolTip()
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.html_preview.setHtml(content)
            else:
                self.html_preview.setPlainText(f"Cannot find file: {filepath}")
        except Exception as e:
            self.html_preview.setPlainText(f"Error opening file: {str(e)}")

    def _open_results_folder(self):
        """Open the results folder."""
        folder = os.path.abspath(self.save_path)
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)

            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':  # macOS
                subprocess.Popen(['open', folder])
            else:  # Linux variants
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening folder: {str(e)}")

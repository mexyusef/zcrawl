"""
Main entry point for the ZCrawl application.
"""
import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from zcrawl.ui.main_window import MainWindow
from zcrawl.resources.stylesheet import StylesheetManager


def setup_logging():
    """Set up application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "zcrawl.log"

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)

    # Log startup
    logger.info("Starting ZCrawl application")

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ZCrawl")
    app.setOrganizationName("ZCrawl Team")
    app.setOrganizationDomain("zcrawl.org")

    # Apply application stylesheet
    StylesheetManager.apply_theme()

    # Create main window
    window = MainWindow()
    window.show()

    # Start application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

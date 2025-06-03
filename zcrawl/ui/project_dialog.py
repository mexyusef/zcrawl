"""
Project dialog for creating or configuring projects.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QDialogButtonBox, QMessageBox, QCheckBox,
    QSpinBox, QComboBox, QGroupBox
)


class ProjectDialog(QDialog):
    """Dialog for creating or configuring a project."""

    def __init__(self, parent=None, title="Project Configuration"):
        """
        Initialize the project dialog.

        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(500, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Project details form
        details_group = QGroupBox("Project Details")
        form_layout = QFormLayout(details_group)

        # Project name
        self.name_input = QLineEdit()
        form_layout.addRow("Name:", self.name_input)

        # Project description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_input)

        layout.addWidget(details_group)

        # Crawling configuration
        crawl_group = QGroupBox("Crawling Configuration")
        crawl_layout = QFormLayout(crawl_group)

        # Max depth
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 10)
        self.max_depth_spin.setValue(2)
        crawl_layout.addRow("Max Depth:", self.max_depth_spin)

        # Max URLs
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(10, 10000)
        self.max_urls_spin.setValue(100)
        self.max_urls_spin.setSingleStep(10)
        crawl_layout.addRow("Max URLs:", self.max_urls_spin)

        # Respect robots.txt
        self.respect_robots_checkbox = QCheckBox()
        self.respect_robots_checkbox.setChecked(True)
        crawl_layout.addRow("Respect robots.txt:", self.respect_robots_checkbox)

        # Same domain only
        self.same_domain_checkbox = QCheckBox()
        self.same_domain_checkbox.setChecked(True)
        crawl_layout.addRow("Same Domain Only:", self.same_domain_checkbox)

        # Request delay
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 30)
        self.delay_spin.setValue(1)
        crawl_layout.addRow("Request Delay (seconds):", self.delay_spin)

        layout.addWidget(crawl_group)

        # Storage configuration
        storage_group = QGroupBox("Storage Configuration")
        storage_layout = QFormLayout(storage_group)

        # Save HTML
        self.save_html_checkbox = QCheckBox()
        self.save_html_checkbox.setChecked(True)
        storage_layout.addRow("Save HTML Content:", self.save_html_checkbox)

        # Export format
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "CSV", "SQLite"])
        storage_layout.addRow("Default Export Format:", self.export_format_combo)

        layout.addWidget(storage_group)

        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def get_project_name(self) -> str:
        """
        Get the project name from the dialog.

        Returns:
            Project name
        """
        return self.name_input.text().strip()

    def get_project_description(self) -> str:
        """
        Get the project description from the dialog.

        Returns:
            Project description
        """
        return self.description_input.toPlainText().strip()

    def get_crawl_config(self) -> dict:
        """
        Get the crawling configuration from the dialog.

        Returns:
            Dictionary of crawling configuration
        """
        return {
            "max_depth": self.max_depth_spin.value(),
            "max_urls": self.max_urls_spin.value(),
            "respect_robots_txt": self.respect_robots_checkbox.isChecked(),
            "same_domain_only": self.same_domain_checkbox.isChecked(),
            "delay": self.delay_spin.value()
        }

    def get_storage_config(self) -> dict:
        """
        Get the storage configuration from the dialog.

        Returns:
            Dictionary of storage configuration
        """
        return {
            "save_html": self.save_html_checkbox.isChecked(),
            "export_format": self.export_format_combo.currentText().lower()
        }

    def set_project_name(self, name: str) -> None:
        """
        Set the project name in the dialog.

        Args:
            name: Project name
        """
        self.name_input.setText(name)

    def set_project_description(self, description: str) -> None:
        """
        Set the project description in the dialog.

        Args:
            description: Project description
        """
        self.description_input.setPlainText(description)

    def set_crawl_config(self, config: dict) -> None:
        """
        Set the crawling configuration in the dialog.

        Args:
            config: Dictionary of crawling configuration
        """
        if "max_depth" in config:
            self.max_depth_spin.setValue(config["max_depth"])

        if "max_urls" in config:
            self.max_urls_spin.setValue(config["max_urls"])

        if "respect_robots_txt" in config:
            self.respect_robots_checkbox.setChecked(config["respect_robots_txt"])

        if "same_domain_only" in config:
            self.same_domain_checkbox.setChecked(config["same_domain_only"])

        if "delay" in config:
            self.delay_spin.setValue(config["delay"])

    def set_storage_config(self, config: dict) -> None:
        """
        Set the storage configuration in the dialog.

        Args:
            config: Dictionary of storage configuration
        """
        if "save_html" in config:
            self.save_html_checkbox.setChecked(config["save_html"])

        if "export_format" in config:
            index = self.export_format_combo.findText(config["export_format"].upper())
            if index >= 0:
                self.export_format_combo.setCurrentIndex(index)

    def accept(self) -> None:
        """Handle dialog acceptance with validation."""
        # Validate project name
        name = self.get_project_name()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return

        super().accept()

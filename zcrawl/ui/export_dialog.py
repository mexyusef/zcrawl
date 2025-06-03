"""
Export dialog for configuring data export options.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QMessageBox, QCheckBox, QComboBox, QGroupBox,
    QFileDialog, QRadioButton, QButtonGroup
)


class ExportDialog(QDialog):
    """Dialog for configuring data export options."""

    def __init__(self, parent=None, title="Export Data"):
        """
        Initialize the export dialog.

        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(500, 350)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Export format
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)

        self.format_group = QButtonGroup(self)

        self.json_radio = QRadioButton("JSON")
        self.format_group.addButton(self.json_radio)
        format_layout.addWidget(self.json_radio)

        self.csv_radio = QRadioButton("CSV")
        self.format_group.addButton(self.csv_radio)
        format_layout.addWidget(self.csv_radio)

        self.sqlite_radio = QRadioButton("SQLite")
        self.format_group.addButton(self.sqlite_radio)
        format_layout.addWidget(self.sqlite_radio)

        # Set JSON as default
        self.json_radio.setChecked(True)

        # Connect format change signals
        self.json_radio.toggled.connect(self._on_format_changed)
        self.csv_radio.toggled.connect(self._on_format_changed)
        self.sqlite_radio.toggled.connect(self._on_format_changed)

        layout.addWidget(format_group)

        # Export options
        self.options_group = QGroupBox("Export Options")
        self.options_layout = QFormLayout(self.options_group)

        # File path
        file_path_layout = QHBoxLayout()

        self.file_path_input = QLineEdit()
        file_path_layout.addWidget(self.file_path_input)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse)
        file_path_layout.addWidget(self.browse_button)

        self.options_layout.addRow("File Path:", file_path_layout)

        # JSON-specific options
        self.json_options_group = QGroupBox("JSON Options")
        json_options_layout = QFormLayout(self.json_options_group)

        self.pretty_print_checkbox = QCheckBox()
        self.pretty_print_checkbox.setChecked(True)
        json_options_layout.addRow("Pretty Print:", self.pretty_print_checkbox)

        self.include_metadata_checkbox = QCheckBox()
        self.include_metadata_checkbox.setChecked(True)
        json_options_layout.addRow("Include Metadata:", self.include_metadata_checkbox)

        self.options_layout.addRow("", self.json_options_group)

        # CSV-specific options
        self.csv_options_group = QGroupBox("CSV Options")
        csv_options_layout = QFormLayout(self.csv_options_group)

        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";", "\\t", "|"])
        csv_options_layout.addRow("Delimiter:", self.delimiter_combo)

        self.include_headers_checkbox = QCheckBox()
        self.include_headers_checkbox.setChecked(True)
        csv_options_layout.addRow("Include Headers:", self.include_headers_checkbox)

        self.quote_strings_checkbox = QCheckBox()
        self.quote_strings_checkbox.setChecked(True)
        csv_options_layout.addRow("Quote Strings:", self.quote_strings_checkbox)

        self.csv_options_group.hide()
        self.options_layout.addRow("", self.csv_options_group)

        # SQLite-specific options
        self.sqlite_options_group = QGroupBox("SQLite Options")
        sqlite_options_layout = QFormLayout(self.sqlite_options_group)

        self.table_name_input = QLineEdit("crawl_data")
        sqlite_options_layout.addRow("Table Name:", self.table_name_input)

        self.replace_table_checkbox = QCheckBox()
        self.replace_table_checkbox.setChecked(True)
        sqlite_options_layout.addRow("Replace Existing Table:", self.replace_table_checkbox)

        self.sqlite_options_group.hide()
        self.options_layout.addRow("", self.sqlite_options_group)

        layout.addWidget(self.options_group)

        # Data selection
        selection_group = QGroupBox("Data Selection")
        selection_layout = QVBoxLayout(selection_group)

        self.all_data_radio = QRadioButton("All Crawled Data")
        self.all_data_radio.setChecked(True)
        selection_layout.addWidget(self.all_data_radio)

        self.selected_data_radio = QRadioButton("Selected URLs Only")
        selection_layout.addWidget(self.selected_data_radio)

        self.current_page_radio = QRadioButton("Current Page Only")
        selection_layout.addWidget(self.current_page_radio)

        layout.addWidget(selection_group)

        # Button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addWidget(self.button_box)

    def _on_format_changed(self):
        """Handle export format change."""
        # Hide all format-specific option groups
        self.json_options_group.hide()
        self.csv_options_group.hide()
        self.sqlite_options_group.hide()

        # Show the appropriate option group
        if self.json_radio.isChecked():
            self.json_options_group.show()
            self.file_path_input.setPlaceholderText("data.json")
        elif self.csv_radio.isChecked():
            self.csv_options_group.show()
            self.file_path_input.setPlaceholderText("data.csv")
        elif self.sqlite_radio.isChecked():
            self.sqlite_options_group.show()
            self.file_path_input.setPlaceholderText("data.db")

    def _on_browse(self):
        """Handle browse button click."""
        file_filter = ""
        if self.json_radio.isChecked():
            file_filter = "JSON Files (*.json);;All Files (*)"
        elif self.csv_radio.isChecked():
            file_filter = "CSV Files (*.csv);;All Files (*)"
        elif self.sqlite_radio.isChecked():
            file_filter = "SQLite Files (*.db *.sqlite);;All Files (*)"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export File", "", file_filter
        )

        if file_path:
            self.file_path_input.setText(file_path)

    def get_export_format(self) -> str:
        """
        Get the selected export format.

        Returns:
            Export format (json, csv, or sqlite)
        """
        if self.json_radio.isChecked():
            return "json"
        elif self.csv_radio.isChecked():
            return "csv"
        elif self.sqlite_radio.isChecked():
            return "sqlite"

        return "json"  # Default

    def get_file_path(self) -> str:
        """
        Get the export file path.

        Returns:
            File path
        """
        return self.file_path_input.text().strip()

    def get_json_options(self) -> dict:
        """
        Get JSON-specific export options.

        Returns:
            Dictionary of JSON options
        """
        return {
            "pretty_print": self.pretty_print_checkbox.isChecked(),
            "include_metadata": self.include_metadata_checkbox.isChecked()
        }

    def get_csv_options(self) -> dict:
        """
        Get CSV-specific export options.

        Returns:
            Dictionary of CSV options
        """
        delimiter = self.delimiter_combo.currentText()
        if delimiter == "\\t":
            delimiter = "\t"

        return {
            "delimiter": delimiter,
            "include_headers": self.include_headers_checkbox.isChecked(),
            "quote_strings": self.quote_strings_checkbox.isChecked()
        }

    def get_sqlite_options(self) -> dict:
        """
        Get SQLite-specific export options.

        Returns:
            Dictionary of SQLite options
        """
        return {
            "table_name": self.table_name_input.text().strip() or "crawl_data",
            "replace_table": self.replace_table_checkbox.isChecked()
        }

    def get_data_selection(self) -> str:
        """
        Get the data selection option.

        Returns:
            Data selection option (all, selected, or current)
        """
        if self.all_data_radio.isChecked():
            return "all"
        elif self.selected_data_radio.isChecked():
            return "selected"
        elif self.current_page_radio.isChecked():
            return "current"

        return "all"  # Default

    def accept(self) -> None:
        """Handle dialog acceptance with validation."""
        # Validate file path
        file_path = self.get_file_path()
        if not file_path:
            QMessageBox.warning(self, "Validation Error", "File path is required.")
            return

        # Validate SQLite table name
        if self.sqlite_radio.isChecked():
            table_name = self.table_name_input.text().strip()
            if not table_name:
                QMessageBox.warning(self, "Validation Error", "Table name is required for SQLite export.")
                return

        super().accept()

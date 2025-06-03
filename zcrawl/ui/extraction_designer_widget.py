"""
Extraction designer widget for creating data extraction templates.
"""
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QTextEdit, QTabWidget,
    QMessageBox, QCheckBox, QSpinBox
)

from zcrawl.extractors.selector_extractor import ExtractionTemplate


class ExtractionDesignerWidget(QWidget):
    """Widget for designing data extraction templates."""

    # Signal emitted when a template is saved
    template_saved = pyqtSignal(ExtractionTemplate)

    def __init__(self, parent=None):
        """
        Initialize the extraction designer widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current template
        self.current_template: Optional[ExtractionTemplate] = None

        # Current URL for testing
        self.current_url: Optional[str] = None

        # Current HTML content for testing
        self.current_html: Optional[str] = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Split into tabs
        self.tab_widget = QTabWidget()

        # Design tab
        design_widget = QWidget()
        design_layout = QVBoxLayout(design_widget)

        # Template settings
        settings_group = QGroupBox("Template Settings")
        settings_layout = QFormLayout(settings_group)

        # Template name
        self.name_input = QLineEdit()
        settings_layout.addRow("Name:", self.name_input)

        # Template description
        self.description_input = QLineEdit()
        settings_layout.addRow("Description:", self.description_input)

        # List extraction settings
        self.is_list_checkbox = QCheckBox("Extract List of Items")
        self.is_list_checkbox.stateChanged.connect(self._on_is_list_changed)
        settings_layout.addRow("", self.is_list_checkbox)

        # List selector
        self.list_selector_input = QLineEdit()
        self.list_selector_input.setEnabled(False)
        settings_layout.addRow("List Selector:", self.list_selector_input)

        # Selector type
        self.selector_type_combo = QComboBox()
        self.selector_type_combo.addItems(["CSS", "XPath"])
        settings_layout.addRow("Selector Type:", self.selector_type_combo)

        design_layout.addWidget(settings_group)

        # Field selectors
        fields_group = QGroupBox("Field Selectors")
        fields_layout = QVBoxLayout(fields_group)

        # Fields table
        self.fields_table = QTableWidget(0, 4)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Selector", "Type", "Attribute"])
        self.fields_table.horizontalHeader().setStretchLastSection(True)
        self.fields_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        fields_layout.addWidget(self.fields_table)

        # Field controls
        field_controls_layout = QHBoxLayout()

        self.add_field_button = QPushButton("Add Field")
        self.add_field_button.clicked.connect(self._on_add_field)
        field_controls_layout.addWidget(self.add_field_button)

        self.remove_field_button = QPushButton("Remove Field")
        self.remove_field_button.clicked.connect(self._on_remove_field)
        field_controls_layout.addWidget(self.remove_field_button)

        fields_layout.addLayout(field_controls_layout)

        design_layout.addWidget(fields_group)

        # Template controls
        template_controls_layout = QHBoxLayout()

        self.new_template_button = QPushButton("New Template")
        self.new_template_button.clicked.connect(self._on_new_template)
        template_controls_layout.addWidget(self.new_template_button)

        self.save_template_button = QPushButton("Save Template")
        self.save_template_button.clicked.connect(self._on_save_template)
        template_controls_layout.addWidget(self.save_template_button)

        self.test_template_button = QPushButton("Test Template")
        self.test_template_button.clicked.connect(self._on_test_template)
        template_controls_layout.addWidget(self.test_template_button)

        design_layout.addLayout(template_controls_layout)

        self.tab_widget.addTab(design_widget, "Design")

        # Test tab
        test_widget = QWidget()
        test_layout = QVBoxLayout(test_widget)

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))

        self.test_url_input = QLineEdit()
        url_layout.addWidget(self.test_url_input)

        self.load_url_button = QPushButton("Load")
        self.load_url_button.clicked.connect(self._on_load_test_url)
        url_layout.addWidget(self.load_url_button)

        test_layout.addLayout(url_layout)

        # Results area
        self.test_results = QTextEdit()
        self.test_results.setReadOnly(True)
        test_layout.addWidget(self.test_results)

        self.tab_widget.addTab(test_widget, "Test")

        layout.addWidget(self.tab_widget)

    def _on_is_list_changed(self, state):
        """
        Handle list extraction checkbox state change.

        Args:
            state: Checkbox state
        """
        self.list_selector_input.setEnabled(state == Qt.CheckState.Checked.value)

    def _on_add_field(self):
        """Handle add field button click."""
        row_count = self.fields_table.rowCount()
        self.fields_table.setRowCount(row_count + 1)

        # Add field name cell
        name_item = QTableWidgetItem(f"field{row_count+1}")
        self.fields_table.setItem(row_count, 0, name_item)

        # Add selector cell
        selector_item = QTableWidgetItem("")
        self.fields_table.setItem(row_count, 1, selector_item)

        # Add type cell (combo box)
        type_combo = QComboBox()
        type_combo.addItems(["CSS", "XPath"])
        self.fields_table.setCellWidget(row_count, 2, type_combo)

        # Add attribute cell
        attribute_item = QTableWidgetItem("")
        self.fields_table.setItem(row_count, 3, attribute_item)

    def _on_remove_field(self):
        """Handle remove field button click."""
        selected_rows = self.fields_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Remove from bottom to top to avoid index shifting problems
        for index in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
            self.fields_table.removeRow(index.row())

    def _on_new_template(self):
        """Handle new template button click."""
        # Check if current template has changes
        if self.current_template:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save the current template before creating a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self._on_save_template()

        # Clear form
        self.name_input.clear()
        self.description_input.clear()
        self.is_list_checkbox.setChecked(False)
        self.list_selector_input.clear()
        self.selector_type_combo.setCurrentIndex(0)

        # Clear fields table
        self.fields_table.setRowCount(0)

        # Clear current template
        self.current_template = None

    def _on_save_template(self):
        """Handle save template button click."""
        # Validate form
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Template name is required.")
            return

        # Create template
        template = ExtractionTemplate(name, self.description_input.text().strip())

        # Set list extraction settings if enabled
        if self.is_list_checkbox.isChecked():
            list_selector = self.list_selector_input.text().strip()
            if not list_selector:
                QMessageBox.warning(self, "Validation Error", "List selector is required when extracting a list.")
                return

            template.set_list_config(
                list_selector,
                self.selector_type_combo.currentText().lower()
            )

        # Add fields
        for row in range(self.fields_table.rowCount()):
            field_name = self.fields_table.item(row, 0).text().strip()
            selector = self.fields_table.item(row, 1).text().strip()
            type_combo = self.fields_table.cellWidget(row, 2)
            selector_type = type_combo.currentText().lower()
            attribute = self.fields_table.item(row, 3).text().strip() or None

            if not field_name or not selector:
                QMessageBox.warning(
                    self, "Validation Error",
                    f"Field name and selector are required for all fields (row {row+1})."
                )
                return

            template.add_field(field_name, selector, selector_type, attribute)

        # Save and emit signal
        self.current_template = template
        self.template_saved.emit(template)

        QMessageBox.information(self, "Template Saved", f"Template '{name}' has been saved successfully.")

    def _on_test_template(self):
        """Handle test template button click."""
        if not self.current_template:
            # Create a temporary template from form data for testing
            try:
                self._on_save_template()
            except:
                QMessageBox.warning(self, "Error", "Please fix template errors before testing.")
                return

        # Switch to test tab
        self.tab_widget.setCurrentIndex(1)

        # If we have a URL and HTML content, run the test
        if self.current_url and self.current_html:
            self._run_template_test()

    def _on_load_test_url(self):
        """Handle load test URL button click."""
        # This would normally fetch the URL and extract HTML
        # For now, just store the URL and notify the user they need an HTML sample
        url = self.test_url_input.text().strip()
        if not url:
            return

        self.current_url = url
        self.test_results.setText("URL loaded. HTML content needs to be provided.")

    def _run_template_test(self):
        """Run the template test on the current HTML content."""
        if not self.current_template or not self.current_html:
            return

        # This would normally create a Page object and extract data
        # For now, just show a placeholder message
        self.test_results.setText("Template testing requires integration with a Page object.")

    def load_template(self, template: ExtractionTemplate):
        """
        Load an existing template into the designer.

        Args:
            template: Template to load
        """
        self.current_template = template

        # Set form values
        self.name_input.setText(template.name)
        self.description_input.setText(template.description or "")

        # Set list extraction settings
        self.is_list_checkbox.setChecked(template.is_list)
        if template.is_list:
            self.list_selector_input.setText(template.list_selector)
            index = self.selector_type_combo.findText(template.selector_type.upper())
            if index >= 0:
                self.selector_type_combo.setCurrentIndex(index)

        # Clear and populate fields table
        self.fields_table.setRowCount(0)

        for name, config in template.extractor.selectors.items():
            row = self.fields_table.rowCount()
            self.fields_table.setRowCount(row + 1)

            # Field name
            self.fields_table.setItem(row, 0, QTableWidgetItem(name))

            # Selector
            self.fields_table.setItem(row, 1, QTableWidgetItem(config["selector"]))

            # Type
            type_combo = QComboBox()
            type_combo.addItems(["CSS", "XPath"])
            index = type_combo.findText(config["type"].upper())
            if index >= 0:
                type_combo.setCurrentIndex(index)
            self.fields_table.setCellWidget(row, 2, type_combo)

            # Attribute
            attribute = config["attribute"] or ""
            self.fields_table.setItem(row, 3, QTableWidgetItem(attribute))

    def set_current_html(self, html: str, url: Optional[str] = None):
        """
        Set the current HTML content for testing.

        Args:
            html: HTML content
            url: URL associated with the HTML (optional)
        """
        self.current_html = html

        if url:
            self.current_url = url
            self.test_url_input.setText(url)

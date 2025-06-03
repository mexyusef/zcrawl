"""
Settings dialog for configuring application-wide settings.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QDialogButtonBox,
    QMessageBox, QCheckBox, QSpinBox, QComboBox, QGroupBox,
    QTabWidget, QTextEdit, QWidget, QFileDialog
)


class SettingsDialog(QDialog):
    """Dialog for configuring application-wide settings."""

    def __init__(self, parent=None):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle("ZCrawl Settings")
        self.resize(500, 400)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Settings tabs
        self.tab_widget = QTabWidget()

        # Crawler settings tab
        crawler_tab = QWidget()
        crawler_layout = QVBoxLayout(crawler_tab)

        # Rate limiting
        rate_group = QGroupBox("Rate Limiting")
        rate_layout = QFormLayout(rate_group)

        self.default_delay_spin = QSpinBox()
        self.default_delay_spin.setRange(0, 60)
        self.default_delay_spin.setValue(1)
        self.default_delay_spin.setSuffix(" seconds")
        rate_layout.addRow("Default Delay:", self.default_delay_spin)

        self.randomize_delay_checkbox = QCheckBox()
        self.randomize_delay_checkbox.setChecked(True)
        rate_layout.addRow("Randomize Delay:", self.randomize_delay_checkbox)

        self.parallel_requests_spin = QSpinBox()
        self.parallel_requests_spin.setRange(1, 10)
        self.parallel_requests_spin.setValue(1)
        rate_layout.addRow("Parallel Requests:", self.parallel_requests_spin)

        crawler_layout.addWidget(rate_group)

        # User agent settings
        agent_group = QGroupBox("User Agent")
        agent_layout = QVBoxLayout(agent_group)

        self.rotate_agent_checkbox = QCheckBox("Rotate User Agents")
        self.rotate_agent_checkbox.setChecked(True)
        agent_layout.addWidget(self.rotate_agent_checkbox)

        self.custom_agents_text = QTextEdit()
        self.custom_agents_text.setPlaceholderText("One user agent per line (leave empty to use default list)")
        agent_layout.addWidget(self.custom_agents_text)

        crawler_layout.addWidget(agent_group)

        # Add crawler tab
        self.tab_widget.addTab(crawler_tab, "Crawler")

        # Proxy settings tab
        proxy_tab = QWidget()
        proxy_layout = QVBoxLayout(proxy_tab)

        self.use_proxy_checkbox = QCheckBox("Use Proxy")
        proxy_layout.addWidget(self.use_proxy_checkbox)

        # Proxy settings group
        proxy_settings_group = QGroupBox("Proxy Settings")
        proxy_settings_layout = QFormLayout(proxy_settings_group)

        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS5"])
        proxy_settings_layout.addRow("Type:", self.proxy_type_combo)

        self.proxy_host_input = QLineEdit()
        proxy_settings_layout.addRow("Host:", self.proxy_host_input)

        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(8080)
        proxy_settings_layout.addRow("Port:", self.proxy_port_spin)

        self.proxy_auth_checkbox = QCheckBox()
        proxy_settings_layout.addRow("Authentication:", self.proxy_auth_checkbox)

        self.proxy_username_input = QLineEdit()
        proxy_settings_layout.addRow("Username:", self.proxy_username_input)

        self.proxy_password_input = QLineEdit()
        self.proxy_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        proxy_settings_layout.addRow("Password:", self.proxy_password_input)

        proxy_layout.addWidget(proxy_settings_group)

        # Add proxy tab
        self.tab_widget.addTab(proxy_tab, "Proxy")

        # Storage settings tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)

        # Project directories
        dir_group = QGroupBox("Project Directories")
        dir_layout = QFormLayout(dir_group)

        self.project_dir_input = QLineEdit("./projects")
        dir_button = QPushButton("Browse...")
        dir_button.clicked.connect(self._on_browse_project_dir)

        dir_input_layout = QHBoxLayout()
        dir_input_layout.addWidget(self.project_dir_input)
        dir_input_layout.addWidget(dir_button)

        dir_layout.addRow("Projects Directory:", dir_input_layout)

        # Data retention
        self.data_retention_spin = QSpinBox()
        self.data_retention_spin.setRange(0, 365)
        self.data_retention_spin.setValue(30)
        self.data_retention_spin.setSuffix(" days")
        self.data_retention_spin.setSpecialValueText("Forever")
        dir_layout.addRow("Data Retention Period:", self.data_retention_spin)

        storage_layout.addWidget(dir_group)

        # Compression settings
        compress_group = QGroupBox("Compression")
        compress_layout = QFormLayout(compress_group)

        self.compress_data_checkbox = QCheckBox()
        self.compress_data_checkbox.setChecked(True)
        compress_layout.addRow("Compress Exported Data:", self.compress_data_checkbox)

        self.compress_level_spin = QSpinBox()
        self.compress_level_spin.setRange(1, 9)
        self.compress_level_spin.setValue(6)
        compress_layout.addRow("Compression Level:", self.compress_level_spin)

        storage_layout.addWidget(compress_group)

        # Save Results tab
        save_tab = QWidget()
        save_layout = QVBoxLayout(save_tab)

        # Auto save settings
        save_group = QGroupBox("Auto Save Settings")
        save_layout_form = QFormLayout(save_group)

        self.auto_save_checkbox = QCheckBox()
        self.auto_save_checkbox.setChecked(False)
        save_layout_form.addRow("Auto Save Results:", self.auto_save_checkbox)

        self.save_interval_spin = QSpinBox()
        self.save_interval_spin.setRange(1, 60)
        self.save_interval_spin.setValue(5)
        self.save_interval_spin.setSuffix(" minutes")
        save_layout_form.addRow("Save Interval:", self.save_interval_spin)

        # Save location
        self.save_location_input = QLineEdit("./results")
        save_dir_button = QPushButton("Browse...")
        save_dir_button.clicked.connect(self._on_browse_save_dir)

        save_dir_layout = QHBoxLayout()
        save_dir_layout.addWidget(self.save_location_input)
        save_dir_layout.addWidget(save_dir_button)

        save_layout_form.addRow("Save Location:", save_dir_layout)

        # Save format selection
        self.save_format_combo = QComboBox()
        self.save_format_combo.addItems(["JSON", "CSV", "HTML", "XML"])
        save_layout_form.addRow("Save Format:", self.save_format_combo)

        self.save_with_content_checkbox = QCheckBox()
        self.save_with_content_checkbox.setChecked(True)
        save_layout_form.addRow("Save with HTML Content:", self.save_with_content_checkbox)

        self.save_screenshots_checkbox = QCheckBox()
        self.save_screenshots_checkbox.setChecked(False)
        save_layout_form.addRow("Save Screenshots:", self.save_screenshots_checkbox)

        save_layout.addWidget(save_group)

        # Add Save Results tab
        self.tab_widget.addTab(save_tab, "Save Results")

        # Add storage tab
        self.tab_widget.addTab(storage_tab, "Storage")

        # UI settings tab
        ui_tab = QWidget()
        ui_layout = QVBoxLayout(ui_tab)

        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        theme_layout.addRow("Application Theme:", self.theme_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(10)
        theme_layout.addRow("Font Size:", self.font_size_spin)

        ui_layout.addWidget(theme_group)

        # UI behavior
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)

        self.confirm_exit_checkbox = QCheckBox()
        self.confirm_exit_checkbox.setChecked(True)
        behavior_layout.addRow("Confirm Exit:", self.confirm_exit_checkbox)

        self.save_layout_checkbox = QCheckBox()
        self.save_layout_checkbox.setChecked(True)
        behavior_layout.addRow("Save Window Layout:", self.save_layout_checkbox)

        self.show_tooltips_checkbox = QCheckBox()
        self.show_tooltips_checkbox.setChecked(True)
        behavior_layout.addRow("Show Tooltips:", self.show_tooltips_checkbox)

        ui_layout.addWidget(behavior_group)

        # Add UI tab
        self.tab_widget.addTab(ui_tab, "UI")

        layout.addWidget(self.tab_widget)

        # Button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.Reset
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._on_apply)
        self.button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self._on_reset)

        layout.addWidget(self.button_box)

        # Connect signals
        self.use_proxy_checkbox.toggled.connect(proxy_settings_group.setEnabled)
        self.proxy_auth_checkbox.toggled.connect(self.proxy_username_input.setEnabled)
        self.proxy_auth_checkbox.toggled.connect(self.proxy_password_input.setEnabled)

        # Initial state
        proxy_settings_group.setEnabled(self.use_proxy_checkbox.isChecked())
        self.proxy_username_input.setEnabled(self.proxy_auth_checkbox.isChecked())
        self.proxy_password_input.setEnabled(self.proxy_auth_checkbox.isChecked())

    def _on_browse_project_dir(self):
        """Handle browse for project directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Projects Directory", self.project_dir_input.text()
        )

        if dir_path:
            self.project_dir_input.setText(dir_path)

    def _on_browse_save_dir(self):
        """Handle browse for save directory."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Save Directory", self.save_location_input.text()
        )

        if dir_path:
            self.save_location_input.setText(dir_path)

    def _on_apply(self):
        """Handle apply button."""
        self._save_settings()
        QMessageBox.information(self, "Settings", "Settings applied successfully.")

    def _on_reset(self):
        """Handle reset button."""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._load_default_settings()

    def _save_settings(self):
        """Save settings."""
        # In a real application, this would save to a settings file
        pass

    def _load_settings(self):
        """Load settings."""
        # In a real application, this would load from a settings file
        pass

    def _load_default_settings(self):
        """Load default settings."""
        # Reset crawler settings
        self.default_delay_spin.setValue(1)
        self.randomize_delay_checkbox.setChecked(True)
        self.parallel_requests_spin.setValue(1)
        self.rotate_agent_checkbox.setChecked(True)
        self.custom_agents_text.clear()

        # Reset proxy settings
        self.use_proxy_checkbox.setChecked(False)
        self.proxy_type_combo.setCurrentIndex(0)
        self.proxy_host_input.clear()
        self.proxy_port_spin.setValue(8080)
        self.proxy_auth_checkbox.setChecked(False)
        self.proxy_username_input.clear()
        self.proxy_password_input.clear()

        # Reset storage settings
        self.project_dir_input.setText("./projects")
        self.data_retention_spin.setValue(30)
        self.compress_data_checkbox.setChecked(True)
        self.compress_level_spin.setValue(6)

        # Reset Save Results settings
        self.auto_save_checkbox.setChecked(False)
        self.save_interval_spin.setValue(5)
        self.save_location_input.setText("./results")
        self.save_format_combo.setCurrentIndex(0)
        self.save_with_content_checkbox.setChecked(True)
        self.save_screenshots_checkbox.setChecked(False)

        # Reset UI settings
        self.theme_combo.setCurrentIndex(0)
        self.font_size_spin.setValue(10)
        self.confirm_exit_checkbox.setChecked(True)
        self.save_layout_checkbox.setChecked(True)
        self.show_tooltips_checkbox.setChecked(True)

    def get_crawler_settings(self) -> dict:
        """
        Get crawler settings.

        Returns:
            Dictionary of crawler settings
        """
        return {
            "default_delay": self.default_delay_spin.value(),
            "randomize_delay": self.randomize_delay_checkbox.isChecked(),
            "parallel_requests": self.parallel_requests_spin.value(),
            "rotate_agent": self.rotate_agent_checkbox.isChecked(),
            "custom_agents": self.custom_agents_text.toPlainText().strip().split("\n") if self.custom_agents_text.toPlainText().strip() else []
        }

    def get_proxy_settings(self) -> dict:
        """
        Get proxy settings.

        Returns:
            Dictionary of proxy settings
        """
        return {
            "use_proxy": self.use_proxy_checkbox.isChecked(),
            "proxy_type": self.proxy_type_combo.currentText(),
            "proxy_host": self.proxy_host_input.text(),
            "proxy_port": self.proxy_port_spin.value(),
            "proxy_auth": self.proxy_auth_checkbox.isChecked(),
            "proxy_username": self.proxy_username_input.text(),
            "proxy_password": self.proxy_password_input.text()
        }

    def get_storage_settings(self) -> dict:
        """
        Get storage settings.

        Returns:
            Dictionary of storage settings
        """
        return {
            "project_dir": self.project_dir_input.text(),
            "data_retention": self.data_retention_spin.value(),
            "compress_data": self.compress_data_checkbox.isChecked(),
            "compress_level": self.compress_level_spin.value()
        }

    def get_save_results_settings(self) -> dict:
        """
        Get save results settings.

        Returns:
            Dictionary of save results settings
        """
        return {
            "auto_save": self.auto_save_checkbox.isChecked(),
            "save_interval": self.save_interval_spin.value(),
            "save_location": self.save_location_input.text(),
            "save_format": self.save_format_combo.currentText(),
            "save_with_content": self.save_with_content_checkbox.isChecked(),
            "save_screenshots": self.save_screenshots_checkbox.isChecked()
        }

    def get_ui_settings(self) -> dict:
        """
        Get UI settings.

        Returns:
            Dictionary of UI settings
        """
        return {
            "theme": self.theme_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "confirm_exit": self.confirm_exit_checkbox.isChecked(),
            "save_layout": self.save_layout_checkbox.isChecked(),
            "show_tooltips": self.show_tooltips_checkbox.isChecked()
        }

    def accept(self) -> None:
        """Handle dialog acceptance."""
        self._save_settings()
        super().accept()

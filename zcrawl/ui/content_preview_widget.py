"""
Content preview widget for displaying web page content.
"""
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QToolBar, QLineEdit, QTabWidget, QTextEdit,
    QSplitter, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction, QKeySequence


class ContentPreviewWidget(QWidget):
    """Widget for previewing web page content."""

    # Signal emitted when a link is clicked in the preview
    link_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialize the content preview widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Current URL
        self.current_url = None

        # Current HTML content
        self.html_content = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Navigation toolbar
        self._create_toolbar(layout)

        # Tab widget for different views
        self.tab_widget = QTabWidget()

        # Web view tab
        self.web_view = QWebEngineView()
        self.web_view.loadStarted.connect(self._on_load_started)
        self.web_view.loadFinished.connect(self._on_load_finished)
        self.tab_widget.addTab(self.web_view, "Web View")

        # HTML source tab
        self.html_view = QTextEdit()
        self.html_view.setReadOnly(True)
        self.html_view.setFont(self._get_monospace_font())
        self.tab_widget.addTab(self.html_view, "HTML Source")

        # Plain text tab
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.tab_widget.addTab(self.text_view, "Plain Text")

        # Info tab
        self.info_view = QTextEdit()
        self.info_view.setReadOnly(True)
        self.tab_widget.addTab(self.info_view, "Page Info")

        layout.addWidget(self.tab_widget)

    def _create_toolbar(self, layout):
        """
        Create the navigation toolbar.

        Args:
            layout: Layout to add toolbar to
        """
        toolbar = QToolBar()

        # Back and forward buttons
        self.back_action = QAction("Back", self)
        self.back_action.triggered.connect(self._on_back)
        self.back_action.setEnabled(False)
        toolbar.addAction(self.back_action)

        self.forward_action = QAction("Forward", self)
        self.forward_action.triggered.connect(self._on_forward)
        self.forward_action.setEnabled(False)
        toolbar.addAction(self.forward_action)

        # Reload button
        self.reload_action = QAction("Reload", self)
        self.reload_action.triggered.connect(self._on_reload)
        self.reload_action.setEnabled(False)
        toolbar.addAction(self.reload_action)

        # URL input
        toolbar.addSeparator()

        self.url_input = QLineEdit()
        self.url_input.returnPressed.connect(self._on_url_entered)
        toolbar.addWidget(self.url_input)

        # Go button
        self.go_action = QAction("Go", self)
        self.go_action.triggered.connect(self._on_url_entered)
        toolbar.addAction(self.go_action)

        layout.addWidget(toolbar)

    def _get_monospace_font(self):
        """
        Get a monospace font for code display.

        Returns:
            QFont object with monospace font
        """
        from PyQt6.QtGui import QFont
        font = QFont("Courier New")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(10)
        return font

    def load_url(self, url: str):
        """
        Load a URL in the preview.

        Args:
            url: URL to load
        """
        self.current_url = url
        self.url_input.setText(url)

        # Load in web view
        self.web_view.load(QUrl(url))

        # Enable navigation buttons
        self.reload_action.setEnabled(True)
        self._update_navigation_buttons()

    def display_html(self, html: str, url: str = None):
        """
        Display HTML content directly.

        Args:
            html: HTML content to display
            url: URL associated with the content (optional)
        """
        if url:
            self.current_url = url
            self.url_input.setText(url)

        self.html_content = html

        # Display in web view
        self.web_view.setHtml(html, QUrl(self.current_url or ""))

        # Display in HTML view
        self.html_view.setText(html)

        # Extract and display plain text
        self._extract_text_from_html(html)

        # Update page info
        self._update_page_info()

        # Enable reload button
        self.reload_action.setEnabled(True)
        self._update_navigation_buttons()

    def display_text(self, text: str, title: str = None):
        """
        Display plain text content.

        Args:
            text: Text content to display
            title: Title for the content (optional)
        """
        self.text_view.setText(text)

        # Switch to text tab
        self.tab_widget.setCurrentWidget(self.text_view)

        # Create simple HTML to display in web view
        html = f"<html><head><title>{title or 'Text View'}</title></head><body><pre>{text}</pre></body></html>"
        self.web_view.setHtml(html)

        # Update HTML view
        self.html_view.setText(html)

        # Update page info
        self._update_page_info()

    def _on_load_started(self):
        """Handle web view load started event."""
        self.setCursor(Qt.CursorShape.WaitCursor)

    def _on_load_finished(self, success: bool):
        """
        Handle web view load finished event.

        Args:
            success: Whether the load was successful
        """
        self.setCursor(Qt.CursorShape.ArrowCursor)

        if success:
            # Extract HTML
            self.web_view.page().toHtml(self._on_html_ready)

            # Update navigation buttons
            self._update_navigation_buttons()
        else:
            # Show error message
            self.html_view.setText("Failed to load page.")
            self.text_view.setText("Failed to load page.")

    def _on_html_ready(self, html: str):
        """
        Handle HTML content extraction from web view.

        Args:
            html: Extracted HTML content
        """
        self.html_content = html
        self.html_view.setText(html)

        # Extract plain text
        self._extract_text_from_html(html)

        # Update page info
        self._update_page_info()

    def _extract_text_from_html(self, html: str):
        """
        Extract plain text from HTML content.

        Args:
            html: HTML content to extract text from
        """
        # Use BeautifulSoup if available
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Get text
            text = soup.get_text()

            # Break into lines and remove leading/trailing space
            lines = (line.strip() for line in text.splitlines())

            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

            # Remove blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)

            self.text_view.setText(text)
        except ImportError:
            # Fallback: just show the HTML
            self.text_view.setPlainText("BeautifulSoup not available for text extraction.")

    def _update_page_info(self):
        """Update the page info tab with metadata."""
        if not self.current_url:
            return

        # Extract info from HTML if available
        title = "Unknown"
        meta_tags = {}

        if self.html_content:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(self.html_content, "html.parser")

                # Get title
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.text.strip()

                # Get meta tags
                for meta in soup.find_all("meta"):
                    name = meta.get("name", meta.get("property", ""))
                    content = meta.get("content", "")
                    if name and content:
                        meta_tags[name] = content
            except ImportError:
                pass

        # Build info text
        info = [
            f"URL: {self.current_url}",
            f"Title: {title}",
            "",
            "Meta Tags:",
        ]

        for name, content in meta_tags.items():
            info.append(f"  {name}: {content}")

        self.info_view.setText("\n".join(info))

    def _update_navigation_buttons(self):
        """Update the state of navigation buttons."""
        if hasattr(self, 'web_view'):
            self.back_action.setEnabled(self.web_view.history().canGoBack())
            self.forward_action.setEnabled(self.web_view.history().canGoForward())

    def _on_back(self):
        """Handle back button click."""
        if self.web_view.history().canGoBack():
            self.web_view.history().back()
            self._update_url_from_web_view()

    def _on_forward(self):
        """Handle forward button click."""
        if self.web_view.history().canGoForward():
            self.web_view.history().forward()
            self._update_url_from_web_view()

    def _on_reload(self):
        """Handle reload button click."""
        self.web_view.reload()

    def _on_url_entered(self):
        """Handle URL entered in the input field."""
        url = self.url_input.text().strip()
        if url:
            # Add http:// if no scheme specified
            if not url.startswith(("http://", "https://")):
                url = "http://" + url

            self.load_url(url)

    def _update_url_from_web_view(self):
        """Update the URL input field from web view URL."""
        url = self.web_view.url().toString()
        self.current_url = url
        self.url_input.setText(url)

    def clear(self):
        """Clear all content in the preview."""
        self.current_url = None
        self.html_content = None

        # Clear URL input
        self.url_input.clear()

        # Clear web view
        self.web_view.setHtml("")

        # Clear text views
        self.html_view.clear()
        self.text_view.clear()
        self.info_view.clear()

        # Disable navigation buttons
        self.reload_action.setEnabled(False)
        self.back_action.setEnabled(False)
        self.forward_action.setEnabled(False)

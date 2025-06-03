"""
Link tree widget for displaying crawled URLs in a tree view.
"""
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QHeaderView, QMenu,
    QAbstractItemView, QLineEdit
)

from urllib.parse import urlparse


class LinkTreeWidget(QWidget):
    """Widget for displaying crawled URLs in a tree view."""

    # Signal emitted when a URL is selected
    url_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Initialize the link tree widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # URL data structures
        self.url_dict: Dict[str, Dict] = {}  # Maps URLs to metadata
        self.domain_dict: Dict[str, List[str]] = {}  # Maps domains to URLs

        self._setup_ui()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search URLs...")
        self.search_box.textChanged.connect(self._filter_tree)
        layout.addWidget(self.search_box)

        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_view.setAlternatingRowColors(True)

        # Set up model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["URL", "Status", "Depth"])
        self.tree_view.setModel(self.model)

        # Configure header
        header = self.tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        # Connect signals
        self.tree_view.clicked.connect(self._on_item_clicked)

        layout.addWidget(self.tree_view)

    def _on_item_clicked(self, index):
        """
        Handle item click in the tree view.

        Args:
            index: Model index that was clicked
        """
        # Get the URL from the item
        if index.isValid():
            item = self.model.itemFromIndex(index)
            parent = item.parent()

            # If we clicked on a URL (leaf node)
            if item.data() and isinstance(item.data(), str):
                url = item.data()
                self.url_selected.emit(url)

    def _show_context_menu(self, position):
        """
        Show context menu for tree items.

        Args:
            position: Position where context menu was requested
        """
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            return

        item = self.model.itemFromIndex(index)
        if not item.data() or not isinstance(item.data(), str):
            return

        url = item.data()

        menu = QMenu()

        # Add actions
        open_action = menu.addAction("Open URL")
        copy_action = menu.addAction("Copy URL")
        add_to_start_action = menu.addAction("Add to Start URLs")

        # Show menu and handle action
        action = menu.exec(self.tree_view.viewport().mapToGlobal(position))

        if action == open_action:
            self.url_selected.emit(url)
        elif action == copy_action:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(url)
        elif action == add_to_start_action:
            # This would need to be connected to project management
            pass

    def add_url(self, url: str, status: str = "Pending", depth: int = 0, parent_url: Optional[str] = None):
        """
        Add a URL to the tree.

        Args:
            url: URL to add
            status: Status of the URL (e.g., "Pending", "Completed", "Failed")
            depth: Crawl depth of the URL
            parent_url: Parent URL that linked to this URL
        """
        # Parse URL to get domain
        parsed = urlparse(url)
        domain = parsed.netloc

        # Store URL data
        if url not in self.url_dict:
            self.url_dict[url] = {
                "status": status,
                "depth": depth,
                "parent_url": parent_url
            }

            # Add to domain dictionary
            if domain not in self.domain_dict:
                self.domain_dict[domain] = []
            self.domain_dict[domain].append(url)

            # Update tree view
            self._rebuild_tree()
        else:
            # Update existing URL
            self.url_dict[url]["status"] = status
            self._update_url_status(url, status)

    def clear(self):
        """Clear all URLs from the tree."""
        self.url_dict.clear()
        self.domain_dict.clear()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["URL", "Status", "Depth"])

    def _rebuild_tree(self):
        """Rebuild the entire tree from URL data."""
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["URL", "Status", "Depth"])

        # Add domains as top-level items
        for domain, urls in self.domain_dict.items():
            domain_item = QStandardItem(domain)

            # Add URLs under domain
            for url in urls:
                url_data = self.url_dict[url]

                # Create path segments
                path_segments = self._get_path_segments(url)

                # Create URL item
                url_item = QStandardItem(path_segments[-1])
                url_item.setData(url)

                status_item = QStandardItem(url_data["status"])
                depth_item = QStandardItem(str(url_data["depth"]))

                # Add items to domain
                domain_item.appendRow([url_item, status_item, depth_item])

            self.model.appendRow(domain_item)

        # Expand all items
        self.tree_view.expandAll()

    def _update_url_status(self, url: str, status: str):
        """
        Update the status of a URL in the tree.

        Args:
            url: URL to update
            status: New status
        """
        # Find the URL in the tree
        for domain_idx in range(self.model.rowCount()):
            domain_item = self.model.item(domain_idx)

            for url_idx in range(domain_item.rowCount()):
                url_item = domain_item.child(url_idx, 0)
                if url_item and url_item.data() == url:
                    status_item = domain_item.child(url_idx, 1)
                    status_item.setText(status)
                    break

    def _filter_tree(self, text: str):
        """
        Filter the tree view based on search text.

        Args:
            text: Search text
        """
        if not text:
            # Show all items
            for domain_idx in range(self.model.rowCount()):
                domain_item = self.model.item(domain_idx)
                self.tree_view.setRowHidden(domain_idx, self.model.indexFromItem(domain_item).parent(), False)

                for url_idx in range(domain_item.rowCount()):
                    url_item = domain_item.child(url_idx, 0)
                    self.tree_view.setRowHidden(url_idx, self.model.indexFromItem(domain_item), False)
            return

        # Filter based on text
        text = text.lower()

        for domain_idx in range(self.model.rowCount()):
            domain_item = self.model.item(domain_idx)
            domain_visible = False

            # Check if domain matches
            if text in domain_item.text().lower():
                domain_visible = True

            # Check URLs in this domain
            for url_idx in range(domain_item.rowCount()):
                url_item = domain_item.child(url_idx, 0)
                url_visible = False

                # Check if URL data matches
                if url_item and url_item.data():
                    if text in url_item.data().lower():
                        url_visible = True

                self.tree_view.setRowHidden(url_idx, self.model.indexFromItem(domain_item), not url_visible)
                domain_visible = domain_visible or url_visible

            self.tree_view.setRowHidden(domain_idx, self.model.indexFromItem(domain_item).parent(), not domain_visible)

    def _get_path_segments(self, url: str) -> List[str]:
        """
        Get path segments from a URL.

        Args:
            url: URL to process

        Returns:
            List of path segments (domain, path1, path2, etc.)
        """
        parsed = urlparse(url)
        domain = parsed.netloc

        # Get path segments
        path = parsed.path.strip('/')
        if not path:
            return [domain, "/"]

        segments = path.split('/')
        filename = segments[-1] if segments else ""

        # Add query if present
        if parsed.query:
            filename += f"?{parsed.query}"

        return [domain] + segments

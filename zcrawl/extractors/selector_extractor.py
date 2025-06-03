"""
Selector-based extractor for web page data extraction.
"""
from typing import Dict, List, Optional, Any, Union


class SelectorExtractor:
    """Extractor that uses CSS or XPath selectors to extract data from a page."""

    def __init__(self):
        """Initialize the selector extractor."""
        # Dictionary of field selectors
        # {field_name: {"selector": selector, "type": "css|xpath", "attribute": attr_name}}
        self.selectors: Dict[str, Dict[str, str]] = {}

    def add_selector(self, field_name: str, selector: str, selector_type: str = "css", attribute: Optional[str] = None):
        """
        Add a selector for a field.

        Args:
            field_name: Name of the field
            selector: CSS or XPath selector
            selector_type: Type of selector ("css" or "xpath")
            attribute: Attribute to extract (e.g., "href", "src")
                       If None, extracts text content
        """
        self.selectors[field_name] = {
            "selector": selector,
            "type": selector_type.lower(),
            "attribute": attribute
        }

    def remove_selector(self, field_name: str):
        """
        Remove a selector.

        Args:
            field_name: Name of the field to remove
        """
        if field_name in self.selectors:
            del self.selectors[field_name]

    def extract(self, html: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from HTML using the defined selectors.

        Args:
            html: HTML content to extract from
            base_url: Base URL for resolving relative URLs (optional)

        Returns:
            Dictionary of extracted data {field_name: value}
        """
        result = {}

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            for field_name, config in self.selectors.items():
                selector = config["selector"]
                selector_type = config["type"]
                attribute = config["attribute"]

                if selector_type == "css":
                    element = soup.select_one(selector)
                    if element:
                        if attribute:
                            value = element.get(attribute, "")
                        else:
                            value = element.get_text(strip=True)
                        result[field_name] = value
                elif selector_type == "xpath":
                    # BeautifulSoup doesn't natively support XPath
                    # This is a placeholder for compatibility
                    result[field_name] = f"XPath extraction not implemented: {selector}"
                else:
                    result[field_name] = None

        except ImportError:
            # Handle case where BeautifulSoup is not available
            for field_name in self.selectors:
                result[field_name] = "BeautifulSoup not available for extraction"

        return result

    def extract_list(self, html: str, list_selector: str, selector_type: str = "css", base_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract a list of items from HTML using the defined selectors.

        Args:
            html: HTML content to extract from
            list_selector: Selector for the list items
            selector_type: Type of selector for the list ("css" or "xpath")
            base_url: Base URL for resolving relative URLs (optional)

        Returns:
            List of dictionaries of extracted data [{field_name: value}]
        """
        results = []

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            if selector_type.lower() == "css":
                items = soup.select(list_selector)

                for item in items:
                    item_data = {}

                    for field_name, config in self.selectors.items():
                        item_selector = config["selector"]
                        item_selector_type = config["type"]
                        attribute = config["attribute"]

                        if item_selector_type == "css":
                            element = item.select_one(item_selector)
                            if element:
                                if attribute:
                                    value = element.get(attribute, "")
                                else:
                                    value = element.get_text(strip=True)
                                item_data[field_name] = value
                            else:
                                item_data[field_name] = None
                        elif item_selector_type == "xpath":
                            # BeautifulSoup doesn't natively support XPath
                            item_data[field_name] = f"XPath extraction not implemented: {item_selector}"
                        else:
                            item_data[field_name] = None

                    results.append(item_data)
            elif selector_type.lower() == "xpath":
                # BeautifulSoup doesn't natively support XPath
                results.append({"error": "XPath list extraction not implemented"})

        except ImportError:
            # Handle case where BeautifulSoup is not available
            results.append({"error": "BeautifulSoup not available for extraction"})

        return results


class ExtractionTemplate:
    """Template for extracting data from web pages."""

    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize the extraction template.

        Args:
            name: Template name
            description: Template description (optional)
        """
        self.name = name
        self.description = description

        # Extractor
        self.extractor = SelectorExtractor()

        # List extraction settings
        self.is_list = False
        self.list_selector = ""
        self.selector_type = "css"

    def add_field(self, field_name: str, selector: str, selector_type: str = "css", attribute: Optional[str] = None):
        """
        Add a field to the template.

        Args:
            field_name: Name of the field
            selector: CSS or XPath selector
            selector_type: Type of selector ("css" or "xpath")
            attribute: Attribute to extract (optional)
        """
        self.extractor.add_selector(field_name, selector, selector_type, attribute)

    def remove_field(self, field_name: str):
        """
        Remove a field from the template.

        Args:
            field_name: Name of the field to remove
        """
        self.extractor.remove_selector(field_name)

    def set_list_config(self, list_selector: str, selector_type: str = "css"):
        """
        Configure the template for list extraction.

        Args:
            list_selector: Selector for the list items
            selector_type: Type of selector ("css" or "xpath")
        """
        self.is_list = True
        self.list_selector = list_selector
        self.selector_type = selector_type.lower()

    def disable_list_extraction(self):
        """Disable list extraction."""
        self.is_list = False

    def extract(self, html: str, base_url: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extract data from HTML using the template.

        Args:
            html: HTML content to extract from
            base_url: Base URL for resolving relative URLs (optional)

        Returns:
            Extracted data - either a dictionary or a list of dictionaries
        """
        if self.is_list:
            return self.extractor.extract_list(html, self.list_selector, self.selector_type, base_url)
        else:
            return self.extractor.extract(html, base_url)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the template to a dictionary for serialization.

        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "description": self.description,
            "is_list": self.is_list,
            "list_selector": self.list_selector,
            "selector_type": self.selector_type,
            "selectors": self.extractor.selectors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractionTemplate':
        """
        Create a template from a dictionary.

        Args:
            data: Dictionary representation of a template

        Returns:
            ExtractionTemplate instance
        """
        template = cls(data["name"], data.get("description"))

        # Set list extraction settings
        if data.get("is_list", False):
            template.set_list_config(data["list_selector"], data["selector_type"])

        # Add selectors
        for field_name, config in data.get("selectors", {}).items():
            template.add_field(
                field_name,
                config["selector"],
                config.get("type", "css"),
                config.get("attribute")
            )

        return template

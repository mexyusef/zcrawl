"""
Project management for organizing crawl sessions and data.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from zcrawl.crawlers.base_crawler import BaseCrawler
from zcrawl.models.url import URL, URLStatus
from zcrawl.models.page import Page
from zcrawl.extractors.selector_extractor import ExtractionTemplate


class Project:
    """
    Manages a crawling project including configuration, state, and output.
    """

    def __init__(self, name: str, base_dir: str = "./projects"):
        """
        Initialize a new or existing project.

        Args:
            name: Project name
            base_dir: Base directory for all projects
        """
        self.name = name
        self.base_dir = base_dir
        self.project_dir = os.path.join(base_dir, name)

        # Project metadata
        self.created_at = datetime.now().isoformat()
        self.last_updated = self.created_at
        self.description = ""

        # Crawl configuration
        self.config = {
            "max_depth": 2,
            "max_urls": 100,
            "respect_robots_txt": True,
            "same_domain_only": True,
            "same_path_only": False,
            "url_patterns": [],
            "excluded_patterns": [],
            "throttling": {
                "default_delay": 1.0,
                "min_delay": 0.5,
                "max_delay": 5.0,
                "jitter": 0.2
            }
        }

        # Crawl state
        self.start_urls = []
        self.completed_urls = set()
        self.extraction_templates = {}

        # Create project directory structure if it doesn't exist
        self._create_project_structure()

        # Try to load existing project
        self._load_project()

    def _create_project_structure(self) -> None:
        """Create the project directory structure."""
        # Main project directory
        os.makedirs(self.project_dir, exist_ok=True)

        # Subdirectories
        for subdir in ["data", "pages", "exports", "templates", "logs"]:
            os.makedirs(os.path.join(self.project_dir, subdir), exist_ok=True)

    def _load_project(self) -> None:
        """Load project from disk if it exists."""
        config_path = os.path.join(self.project_dir, "project.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load project metadata
                self.created_at = data.get("created_at", self.created_at)
                self.last_updated = data.get("last_updated", self.last_updated)
                self.description = data.get("description", "")

                # Load configuration
                self.config = data.get("config", self.config)

                # Load crawl state
                self.start_urls = data.get("start_urls", [])
                self.completed_urls = set(data.get("completed_urls", []))

                # Load extraction templates
                templates_data = data.get("extraction_templates", {})
                for template_name, template_data in templates_data.items():
                    self.extraction_templates[template_name] = ExtractionTemplate.from_dict(template_data)

            except Exception as e:
                print(f"Error loading project: {str(e)}")

    def save(self) -> None:
        """Save project configuration and state to disk."""
        self.last_updated = datetime.now().isoformat()

        # Prepare data for serialization
        data = {
            "name": self.name,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "description": self.description,
            "config": self.config,
            "start_urls": self.start_urls,
            "completed_urls": list(self.completed_urls),
            "extraction_templates": {
                name: template.to_dict()
                for name, template in self.extraction_templates.items()
            }
        }

        # Save to file
        config_path = os.path.join(self.project_dir, "project.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def set_description(self, description: str) -> None:
        """
        Set project description.

        Args:
            description: Project description
        """
        self.description = description
        self.save()

    def update_config(self, **kwargs) -> None:
        """
        Update project configuration.

        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

        self.save()

    def add_start_url(self, url: str) -> None:
        """
        Add a start URL for crawling.

        Args:
            url: URL to start crawling from
        """
        if url not in self.start_urls:
            self.start_urls.append(url)
            self.save()

    def remove_start_url(self, url: str) -> bool:
        """
        Remove a start URL.

        Args:
            url: URL to remove

        Returns:
            True if removed, False if not found
        """
        if url in self.start_urls:
            self.start_urls.remove(url)
            self.save()
            return True
        return False

    def add_extraction_template(self, template: ExtractionTemplate) -> None:
        """
        Add an extraction template to the project.

        Args:
            template: ExtractionTemplate instance
        """
        self.extraction_templates[template.name] = template
        self.save()

    def remove_extraction_template(self, template_name: str) -> bool:
        """
        Remove an extraction template.

        Args:
            template_name: Name of template to remove

        Returns:
            True if removed, False if not found
        """
        if template_name in self.extraction_templates:
            del self.extraction_templates[template_name]
            self.save()
            return True
        return False

    def get_extraction_template(self, template_name: str) -> Optional[ExtractionTemplate]:
        """
        Get an extraction template by name.

        Args:
            template_name: Name of template to get

        Returns:
            ExtractionTemplate or None if not found
        """
        return self.extraction_templates.get(template_name)

    def save_page(self, page: Page) -> None:
        """
        Save a crawled page to the project.

        Args:
            page: Page to save
        """
        # Add to completed URLs
        self.completed_urls.add(page.url.url)

        # Create a unique filename
        url_hash = str(hash(page.url.url))
        timestamp = int(time.time())
        filename = f"{url_hash}_{timestamp}.json"

        # Save page data
        page_data = {
            "url": page.url.url,
            "fetched_at": page.fetched_at.isoformat(),
            "status_code": page.status_code,
            "title": page.title,
            "content_type": page.content_type,
            "links": page.links,
            "images": page.images,
            "scripts": page.scripts,
            "stylesheets": page.stylesheets,
            "meta_tags": page.meta_tags
        }

        # Save HTML content separately if it exists
        if page.html_content:
            html_path = os.path.join(self.project_dir, "pages", f"{url_hash}_{timestamp}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.html_content)

        # Save page data
        page_path = os.path.join(self.project_dir, "data", filename)
        with open(page_path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2)

    def extract_data(self, page: Page, template_name: str) -> Any:
        """
        Extract data from a page using a template.

        Args:
            page: Page to extract data from
            template_name: Name of extraction template to use

        Returns:
            Extracted data or None if template not found
        """
        template = self.get_extraction_template(template_name)
        if not template:
            return None

        return template.extract(page)

    def save_extracted_data(self, data: Any, template_name: str, format: str = "json") -> str:
        """
        Save extracted data to a file.

        Args:
            data: Data to save
            template_name: Name of template used for extraction
            format: Output format (json, csv, etc.)

        Returns:
            Path to saved file
        """
        timestamp = int(time.time())
        filename = f"{template_name}_{timestamp}.{format}"
        file_path = os.path.join(self.project_dir, "exports", filename)

        if format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            # TODO: Implement CSV export
            pass

        return file_path

    @staticmethod
    def list_projects(base_dir: str = "./projects") -> List[str]:
        """
        List all existing projects.

        Args:
            base_dir: Base directory for projects

        Returns:
            List of project names
        """
        if not os.path.exists(base_dir):
            return []

        return [d for d in os.listdir(base_dir)
                if os.path.isdir(os.path.join(base_dir, d))
                and os.path.exists(os.path.join(base_dir, d, "project.json"))]

    @classmethod
    def load(cls, name: str, base_dir: str = "./projects") -> Optional["Project"]:
        """
        Load an existing project.

        Args:
            name: Project name
            base_dir: Base directory for projects

        Returns:
            Project instance or None if not found
        """
        project_path = os.path.join(base_dir, name, "project.json")
        if not os.path.exists(project_path):
            return None

        return cls(name, base_dir)

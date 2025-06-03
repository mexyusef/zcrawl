"""
Page data model for storing crawled page content and metadata.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse
import time

from zcrawl.models.url import URL


@dataclass
class Page:
    """Represents a crawled web page with its content and metadata."""

    url: URL
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    title: Optional[str] = None
    fetched_at: datetime = field(default_factory=datetime.now)
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    stylesheets: List[str] = field(default_factory=list)
    forms: List[Dict] = field(default_factory=list)
    meta_tags: Dict[str, str] = field(default_factory=dict)
    crawl_time: float = field(default_factory=time.time)

    @property
    def domain(self) -> str:
        """Get the domain of the page."""
        return self.url.domain

    @property
    def is_success(self) -> bool:
        """Check if the page was successfully fetched."""
        return self.status_code == 200

    @property
    def is_redirect(self) -> bool:
        """Check if the page is a redirect."""
        return self.status_code is not None and 300 <= self.status_code < 400

    @property
    def is_error(self) -> bool:
        """Check if the page fetch resulted in an error."""
        return self.status_code is None or self.status_code >= 400

    @property
    def is_html(self) -> bool:
        """Check if the page is HTML."""
        return self.content_type is not None and 'text/html' in self.content_type.lower()

    @property
    def word_count(self) -> int:
        """Count the number of words in the text content."""
        if not self.text_content:
            return 0
        return len(self.text_content.split())

    def get_internal_links(self) -> List[str]:
        """Get links that point to the same domain."""
        if not self.links:
            return []

        page_domain = self.domain
        return [link for link in self.links if self._is_same_domain(link, page_domain)]

    def get_external_links(self) -> List[str]:
        """Get links that point to different domains."""
        if not self.links:
            return []

        page_domain = self.domain
        return [link for link in self.links if not self._is_same_domain(link, page_domain)]

    def _is_same_domain(self, link: str, page_domain: str) -> bool:
        """
        Check if a link is on the same domain as the page.

        Args:
            link: URL to check
            page_domain: Domain of the current page

        Returns:
            True if same domain
        """
        try:
            parsed = urlparse(link)
            # Handle relative URLs
            if not parsed.netloc:
                return True
            return parsed.netloc == page_domain
        except:
            return False

    def serialize(self) -> Dict:
        """
        Convert the page to a serializable dictionary.

        Returns:
            Dict representation of the page
        """
        return {
            "url": self.url.url,
            "title": self.title,
            "fetched_at": self.fetched_at.isoformat(),
            "status_code": self.status_code,
            "content_type": self.content_type,
            "headers": self.headers,
            "links_count": len(self.links),
            "images_count": len(self.images),
            "word_count": self.word_count,
        }

    def __str__(self) -> str:
        """String representation of the page."""
        return f"Page: {self.url}"

    def __repr__(self) -> str:
        """Debug representation of the page."""
        return f"Page(url={self.url}, status_code={self.status_code})"

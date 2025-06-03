"""
URL data model for tracking URLs during crawling.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, urljoin, urlunparse


class URLStatus(Enum):
    """Status of a URL in the crawling process."""
    PENDING = "pending"
    CRAWLING = "crawling"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class URL:
    """Data model representing a URL in the crawling process."""

    url: str
    depth: int = 0
    status: URLStatus = URLStatus.PENDING
    parent_url: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.now)
    last_crawled: Optional[datetime] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    content_type: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

    # Parsed components for quick access
    _scheme: Optional[str] = None
    _netloc: Optional[str] = None
    _path: Optional[str] = None
    _params: Optional[str] = None
    _query: Optional[str] = None
    _fragment: Optional[str] = None

    def __post_init__(self):
        """Parse URL components after initialization."""
        self._parse_url()

    def _parse_url(self) -> None:
        """Parse URL into components."""
        parsed = urlparse(self.url)
        self._scheme = parsed.scheme
        self._netloc = parsed.netloc
        self._path = parsed.path
        self._params = parsed.params
        self._query = parsed.query
        self._fragment = parsed.fragment

    @property
    def domain(self) -> str:
        """Get the domain part of the URL."""
        return self._netloc

    @property
    def base_url(self) -> str:
        """Get the base URL (scheme + netloc)."""
        return f"{self._scheme}://{self._netloc}"

    @property
    def path(self) -> str:
        """Get the path part of the URL."""
        return self._path

    @property
    def is_same_domain(self, other_url: str) -> bool:
        """Check if another URL is on the same domain."""
        other_parsed = urlparse(other_url)
        return self._netloc == other_parsed.netloc

    def join(self, relative_url: str) -> str:
        """
        Join this URL with a relative URL.

        Args:
            relative_url: Relative URL to join with this URL

        Returns:
            Absolute URL
        """
        return urljoin(self.url, relative_url)

    def set_status(self, status: URLStatus, error: Optional[str] = None) -> None:
        """
        Update the status of this URL.

        Args:
            status: New status
            error: Optional error message if status is FAILED
        """
        self.status = status
        if status == URLStatus.FAILED and error:
            self.error_message = error
        elif status == URLStatus.COMPLETED:
            self.last_crawled = datetime.now()

    def normalize(self) -> None:
        """Normalize the URL to avoid duplicates."""
        # Remove trailing slash
        url = self.url.rstrip('/')

        # Remove fragment
        parsed = urlparse(url)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # No fragment
        ))

        self.url = normalized
        self._parse_url()


class URLSet:
    """A set-like collection of URLs that avoids duplicates based on normalized URLs."""

    def __init__(self):
        """Initialize an empty URL set."""
        self._urls: Dict[str, URL] = {}
        self._seen_urls: Set[str] = set()

    def add(self, url: URL) -> bool:
        """
        Add a URL to the set if it doesn't already exist.

        Args:
            url: URL to add

        Returns:
            True if added, False if already exists
        """
        # Normalize URL for comparison
        url.normalize()

        if url.url in self._seen_urls:
            return False

        self._urls[url.url] = url
        self._seen_urls.add(url.url)
        return True

    def get(self, url_str: str) -> Optional[URL]:
        """
        Get a URL object by its string representation.

        Args:
            url_str: URL string

        Returns:
            URL object or None if not found
        """
        return self._urls.get(url_str)

    def get_all(self) -> List[URL]:
        """Get all URLs in the set."""
        return list(self._urls.values())

    def get_by_status(self, status: URLStatus) -> List[URL]:
        """
        Get URLs with the specified status.

        Args:
            status: Status to filter by

        Returns:
            List of matching URLs
        """
        return [url for url in self._urls.values() if url.status == status]

    def contains(self, url_str: str) -> bool:
        """
        Check if the set contains a URL.

        Args:
            url_str: URL string to check

        Returns:
            True if URL exists in set
        """
        # Normalize URL for comparison
        parsed = urlparse(url_str)
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''
        )).rstrip('/')

        return normalized in self._seen_urls

    def __len__(self) -> int:
        """Get the number of URLs in the set."""
        return len(self._urls)


class URL:
    """Class representing a URL in the crawler."""

    def __init__(self, url: str, parent_url: Optional[str] = None, depth: int = 0):
        """
        Initialize a URL.

        Args:
            url: URL string
            parent_url: Parent URL string or None if root URL
            depth: Crawl depth (0 for start URL)
        """
        self.url = url
        self.parent_url = parent_url
        self.depth = depth

    def __str__(self) -> str:
        """String representation of URL."""
        return self.url

    def __repr__(self) -> str:
        """Debug representation of URL."""
        return f"URL(url='{self.url}', parent_url='{self.parent_url}', depth={self.depth})"

    def __eq__(self, other) -> bool:
        """
        Check if two URLs are equal.

        Args:
            other: Other URL to compare

        Returns:
            True if URLs are equal
        """
        if not isinstance(other, URL):
            return False
        return self.url == other.url

    def __hash__(self) -> int:
        """
        Get hash of URL.

        Returns:
            Hash value
        """
        return hash(self.url)

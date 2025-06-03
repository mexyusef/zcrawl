"""
Base crawler class that other crawlers extend.
"""
import abc
import threading
import logging
import time
from typing import Dict, List, Optional, Set, Callable
from urllib.parse import urlparse
import random
from queue import Queue, Empty

from zcrawl.models.url import URL
from zcrawl.models.page import Page


class UserAgentManager:
    """Manager for rotating user agents."""

    DEFAULT_USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ]

    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize the user agent manager.

        Args:
            user_agents: List of user agents to use (optional)
        """
        self.user_agents = user_agents or self.DEFAULT_USER_AGENTS
        self.current_index = 0

    def get_next(self) -> str:
        """
        Get the next user agent in the rotation.

        Returns:
            User agent string
        """
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent

    def get_random(self) -> str:
        """
        Get a random user agent.

        Returns:
            User agent string
        """
        return random.choice(self.user_agents)


class BaseCrawler(abc.ABC):
    """Base crawler class that defines the crawler interface."""

    def __init__(self, max_depth: int = 2, same_domain_only: bool = True,
                 same_path_only: bool = False, respect_robots_txt: bool = True,
                 request_delay: float = 1.0):
        """
        Initialize the base crawler.

        Args:
            max_depth: Maximum depth to crawl
            same_domain_only: Only crawl URLs on the same domain
            same_path_only: Only crawl URLs under the same path
            respect_robots_txt: Whether to respect robots.txt
            request_delay: Delay between requests in seconds
        """
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.same_path_only = same_path_only
        self.respect_robots_txt = respect_robots_txt
        self.request_delay = request_delay

        # Crawler state
        self.running = False
        self.paused = False

        # URL tracking
        self.url_queue = Queue()
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.disallowed_urls: Set[str] = set()

        # URL objects by URL string
        self.url_objects: Dict[str, URL] = {}

        # Pages by URL string
        self.pages: Dict[str, Page] = {}

        # Robots.txt cache by domain
        self.robots_cache: Dict[str, Set[str]] = {}

        # User agent manager
        self.user_agent_manager = UserAgentManager()

        # Crawler thread
        self.crawler_thread = None

        # Loggers
        self.logger = logging.getLogger(__name__)

    def start(self, start_url: str) -> None:
        """
        Start crawling from a URL.

        Args:
            start_url: Initial URL to crawl
        """
        if self.running:
            self.logger.warning("Crawler is already running")
            return

        # Reset crawler state
        self.running = True
        self.paused = False

        # Add start URL to queue
        self._add_url(start_url)

        # Start crawler thread
        self.crawler_thread = threading.Thread(target=self._crawl_loop)
        self.crawler_thread.daemon = True
        self.crawler_thread.start()

    def pause(self) -> None:
        """Pause the crawler."""
        self.paused = True
        self.logger.info("Crawler paused")

    def resume(self) -> None:
        """Resume a paused crawler."""
        self.paused = False
        self.logger.info("Crawler resumed")

    def stop(self) -> None:
        """Stop the crawler."""
        self.running = False
        self.paused = False

        if self.crawler_thread and self.crawler_thread.is_alive():
            self.crawler_thread.join(2.0)  # Wait for the thread to finish

        self.logger.info("Crawler stopped")

    def _crawl_loop(self) -> None:
        """Main crawling loop."""
        while self.running:
            # Check if paused
            if self.paused:
                time.sleep(0.5)
                continue

            try:
                # Get the next URL to crawl
                url = self.url_queue.get(timeout=1.0)

                # Skip if already visited
                if url.url in self.visited_urls:
                    self.url_queue.task_done()
                    continue

                # Add to visited set
                self.visited_urls.add(url.url)

                # Check if exceeds max depth
                if url.depth > self.max_depth:
                    self.url_queue.task_done()
                    continue

                # Fetch the page
                page = self._fetch_page(url)

                # Process the page if fetch was successful
                if page:
                    self.pages[url.url] = page
                    self._process_page(page)
                else:
                    self.failed_urls.add(url.url)

                # Delay between requests
                time.sleep(self.request_delay)

                # Mark task as done
                self.url_queue.task_done()

            except Empty:
                # Queue is empty, check if we should continue running
                if self.url_queue.empty() and self.running:
                    self.logger.info("Crawl queue is empty, stopping")
                    self.running = False

            except Exception as e:
                self.logger.error(f"Error in crawl loop: {str(e)}")

    @abc.abstractmethod
    def _fetch_page(self, url: URL) -> Optional[Page]:
        """
        Fetch a page.

        Args:
            url: URL to fetch

        Returns:
            Page object or None if failed
        """
        pass

    @abc.abstractmethod
    def _process_page(self, page: Page) -> None:
        """
        Process a fetched page.

        Args:
            page: Page to process
        """
        pass

    def _add_url(self, url: str, parent_url: Optional[URL] = None) -> bool:
        """
        Add a URL to the crawler queue if it meets crawling criteria.

        Args:
            url: URL to add
            parent_url: Parent URL that linked to this URL

        Returns:
            True if the URL was added, False otherwise
        """
        # Skip if already visited or in queue
        if url in self.visited_urls or url in self.url_objects:
            return False

        # Parse URL
        parsed = urlparse(url)

        # Skip invalid URLs
        if not parsed.scheme or not parsed.netloc:
            return False

        # Skip if not http/https
        if parsed.scheme not in ("http", "https"):
            return False

        # Check if same domain
        if self.same_domain_only and parent_url:
            parent_parsed = urlparse(parent_url.url)
            if parsed.netloc != parent_parsed.netloc:
                return False

        # Check if same path
        if self.same_path_only and parent_url:
            parent_parsed = urlparse(parent_url.url)
            if not parsed.path.startswith(parent_parsed.path):
                return False

        # Calculate depth
        depth = 0
        if parent_url:
            depth = parent_url.depth + 1

        # Create URL object
        url_obj = URL(url=url, parent_url=parent_url.url if parent_url else None, depth=depth)

        # Store URL object
        self.url_objects[url] = url_obj

        # Add to queue
        self.url_queue.put(url_obj)

        return True

    def get_visited_count(self) -> int:
        """
        Get the number of visited URLs.

        Returns:
            Number of visited URLs
        """
        return len(self.visited_urls)

    def get_queued_count(self) -> int:
        """
        Get the number of queued URLs.

        Returns:
            Number of queued URLs
        """
        return self.url_queue.qsize()

    def get_failed_count(self) -> int:
        """
        Get the number of failed URLs.

        Returns:
            Number of failed URLs
        """
        return len(self.failed_urls)

    def clear(self) -> None:
        """Clear all crawler state."""
        # Stop if running
        if self.running:
            self.stop()

        # Clear URL tracking
        while not self.url_queue.empty():
            self.url_queue.get()
            self.url_queue.task_done()

        self.visited_urls.clear()
        self.failed_urls.clear()
        self.disallowed_urls.clear()
        self.url_objects.clear()
        self.pages.clear()
        self.robots_cache.clear()

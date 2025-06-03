"""
HTTP-based crawler implementation using requests.
"""
import logging
import time
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style, init

from zcrawl.crawlers.base_crawler import BaseCrawler
from zcrawl.models.url import URL
from zcrawl.models.page import Page


# Initialize colorama
init(autoreset=True)


class ColoramaLogHandler(logging.Handler):
    """Custom logging handler that uses colorama for colored console output."""

    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Back.WHITE + Style.BRIGHT
    }

    def emit(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        prefix = f"{time.strftime('%H:%M:%S')} "

        if record.levelno == logging.INFO:
            prefix += f"{Fore.GREEN}[INFO]{Style.RESET_ALL} "
        elif record.levelno == logging.DEBUG:
            prefix += f"{Fore.CYAN}[DEBUG]{Style.RESET_ALL} "
        elif record.levelno == logging.WARNING:
            prefix += f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} "
        elif record.levelno == logging.ERROR:
            prefix += f"{Fore.RED}[ERROR]{Style.RESET_ALL} "
        elif record.levelno == logging.CRITICAL:
            prefix += f"{Fore.RED}{Back.WHITE}[CRITICAL]{Style.RESET_ALL} "

        message = f"{prefix}{color}{self.format(record)}{Style.RESET_ALL}"
        print(message)


class HTTPCrawler(BaseCrawler):
    """HTTP-based crawler using requests and BeautifulSoup."""

    def __init__(self, **kwargs):
        """
        Initialize the HTTP crawler.

        Args:
            **kwargs: Arguments to pass to BaseCrawler
        """
        super().__init__(**kwargs)
        self.session = requests.Session()

        # Set up colorama logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicate logs
        if self.logger.handlers:
            self.logger.handlers.clear()

        # Add colorama handler
        colorama_handler = ColoramaLogHandler()
        self.logger.addHandler(colorama_handler)

        self.logger.info(f"{Fore.CYAN}HTTPCrawler initialized{Style.RESET_ALL}")

    def start(self, start_url: str) -> None:
        """
        Start crawling from a URL.

        Args:
            start_url: Initial URL to crawl
        """
        self.logger.info(f"{Fore.GREEN}Starting crawl from: {Fore.CYAN}{start_url}{Style.RESET_ALL}")
        super().start(start_url)

    def stop(self) -> None:
        """Stop the crawler."""
        self.logger.info(f"{Fore.YELLOW}Stopping crawler...{Style.RESET_ALL}")
        super().stop()
        self.logger.info(f"{Fore.GREEN}Crawler stopped. Total pages: {len(self.visited_urls)}{Style.RESET_ALL}")

    def _fetch_page(self, url: URL) -> Optional[Page]:
        """
        Fetch a page using HTTP requests.

        Args:
            url: URL to fetch

        Returns:
            Page object or None if failed
        """
        try:
            self.logger.info(f"{Fore.CYAN}Fetching page: {url.url}{Style.RESET_ALL}")

            # Get user agent
            user_agent = self.user_agent_manager.get_next()
            headers = {"User-Agent": user_agent}
            self.logger.debug(f"Using User-Agent: {user_agent}")

            # Send request
            start_time = time.time()
            response = self.session.get(url.url, headers=headers, timeout=30)
            fetch_time = time.time() - start_time

            # Create page object
            page = Page(url=url)
            page.status_code = response.status_code
            page.headers = dict(response.headers)
            page.content_type = response.headers.get("Content-Type", "")

            self.logger.info(f"{Fore.GREEN}Received response: {Fore.CYAN}{response.status_code}{Style.RESET_ALL} ({round(fetch_time, 2)}s)")

            # Only process HTML content
            if response.status_code == 200 and page.is_html:
                self.logger.info(f"{Fore.GREEN}Processing HTML content ({len(response.text)} bytes)")
                page.html_content = response.text

                # Parse HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract title
                title_tag = soup.find("title")
                if title_tag:
                    page.title = title_tag.text.strip()
                    self.logger.info(f"{Fore.GREEN}Page title: {Fore.CYAN}{page.title}{Style.RESET_ALL}")

                # Extract text content
                texts = soup.find_all(text=True)
                visible_texts = [t.strip() for t in texts if t.parent.name not in ['style', 'script', 'head', 'meta']]
                page.text_content = " ".join([t for t in visible_texts if t])

                # Extract links
                links = self._extract_links_from_soup(soup, url.url)
                page.links = links
                self.logger.info(f"{Fore.GREEN}Extracted {Fore.CYAN}{len(links)}{Fore.GREEN} links{Style.RESET_ALL}")

                # Extract images
                images = self._extract_images_from_soup(soup, url.url)
                page.images = images
                self.logger.info(f"{Fore.GREEN}Extracted {Fore.CYAN}{len(images)}{Fore.GREEN} images{Style.RESET_ALL}")

                # Extract scripts
                scripts = self._extract_scripts_from_soup(soup, url.url)
                page.scripts = scripts
                self.logger.debug(f"Extracted {len(scripts)} scripts")

                # Extract stylesheets
                stylesheets = self._extract_stylesheets_from_soup(soup, url.url)
                page.stylesheets = stylesheets
                self.logger.debug(f"Extracted {len(stylesheets)} stylesheets")

                # Extract forms
                forms = self._extract_forms_from_soup(soup, url.url)
                page.forms = forms
                self.logger.debug(f"Extracted {len(forms)} forms")

                # Extract meta tags
                meta_tags = self._extract_meta_tags_from_soup(soup)
                page.meta_tags = meta_tags
                self.logger.debug(f"Extracted {len(meta_tags)} meta tags")
            else:
                if response.status_code != 200:
                    self.logger.warning(f"{Fore.YELLOW}Non-200 status code: {response.status_code}{Style.RESET_ALL}")
                else:
                    self.logger.warning(f"{Fore.YELLOW}Non-HTML content: {page.content_type}{Style.RESET_ALL}")

            return page

        except requests.exceptions.Timeout:
            self.logger.error(f"{Fore.RED}Timeout error fetching {url.url}{Style.RESET_ALL}")
            return None
        except requests.exceptions.ConnectionError:
            self.logger.error(f"{Fore.RED}Connection error fetching {url.url}{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error fetching {url.url}: {str(e)}{Style.RESET_ALL}")
            return None

    def _process_page(self, page: Page) -> None:
        """
        Process a fetched page, extract links and add them to the crawl queue.

        Args:
            page: Page to process
        """
        # Only process HTML pages
        if not page.is_html:
            self.logger.warning(f"{Fore.YELLOW}Skipping non-HTML page: {page.url.url}{Style.RESET_ALL}")
            return

        self.logger.info(f"{Fore.GREEN}Processing page: {Fore.CYAN}{page.url.url}{Style.RESET_ALL}")

        # Add discovered links to crawl queue
        links_added = 0
        for link in page.links:
            if self._add_url(link, page.url):
                links_added += 1

        self.logger.info(f"{Fore.GREEN}Added {Fore.CYAN}{links_added}{Fore.GREEN} new URLs to the crawl queue{Style.RESET_ALL}")

        try:
            self.logger.info(f"{Fore.GREEN}Queue size: {Fore.CYAN}{self.url_queue.qsize()}{Fore.GREEN}, Visited: {Fore.CYAN}{len(self.visited_urls)}{Style.RESET_ALL}")
        except Exception as e:
            self.logger.error(f"{Fore.RED}Error in crawl loop: {str(e)}{Style.RESET_ALL}")

    def _add_url(self, url: str, parent_url: Optional[URL] = None) -> bool:
        """
        Add a URL to the crawler queue if it meets crawling criteria.

        Args:
            url: URL to add
            parent_url: Parent URL that linked to this URL

        Returns:
            True if the URL was added, False otherwise
        """
        result = super()._add_url(url, parent_url)
        if not result:
            self.logger.debug(f"Skipped URL (already visited or filtered): {url}")
        return result

    def _extract_links_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract links from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of URLs
        """
        links = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()

            # Skip empty links, fragments, javascript, mailto
            if not href or href.startswith(("#", "javascript:", "mailto:")):
                continue

            # Make absolute URL
            absolute_url = urljoin(base_url, href)

            # Normalize
            parsed = urlparse(absolute_url)
            if not parsed.scheme:
                continue

            # Add to list
            links.append(absolute_url)

        return links

    def _extract_images_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract image URLs from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image URLs
        """
        images = []

        for img_tag in soup.find_all("img", src=True):
            src = img_tag["src"].strip()

            # Skip empty sources or data URLs
            if not src or src.startswith("data:"):
                continue

            # Make absolute URL
            absolute_url = urljoin(base_url, src)

            # Add to list
            images.append(absolute_url)

        return images

    def _extract_scripts_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract script URLs from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of script URLs
        """
        scripts = []

        for script_tag in soup.find_all("script", src=True):
            src = script_tag["src"].strip()

            # Skip empty sources
            if not src:
                continue

            # Make absolute URL
            absolute_url = urljoin(base_url, src)

            # Add to list
            scripts.append(absolute_url)

        return scripts

    def _extract_stylesheets_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract stylesheet URLs from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of stylesheet URLs
        """
        stylesheets = []

        for link_tag in soup.find_all("link", rel="stylesheet", href=True):
            href = link_tag["href"].strip()

            # Skip empty sources
            if not href:
                continue

            # Make absolute URL
            absolute_url = urljoin(base_url, href)

            # Add to list
            stylesheets.append(absolute_url)

        return stylesheets

    def _extract_forms_from_soup(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract forms from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative URLs

        Returns:
            List of form dictionaries
        """
        forms = []

        for form_tag in soup.find_all("form"):
            form = {
                "action": urljoin(base_url, form_tag.get("action", "")),
                "method": form_tag.get("method", "get").upper(),
                "inputs": []
            }

            # Extract inputs
            for input_tag in form_tag.find_all("input"):
                input_type = input_tag.get("type", "text")
                input_name = input_tag.get("name", "")

                if input_name:
                    form["inputs"].append({
                        "type": input_type,
                        "name": input_name,
                        "value": input_tag.get("value", "")
                    })

            forms.append(form)

        return forms

    def _extract_meta_tags_from_soup(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract meta tags from BeautifulSoup object.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dictionary of meta tag name/property to content
        """
        meta_tags = {}

        for meta_tag in soup.find_all("meta"):
            # Get name or property
            name = meta_tag.get("name", "")
            if not name:
                name = meta_tag.get("property", "")

            # Get content
            content = meta_tag.get("content", "")

            if name and content:
                meta_tags[name] = content

        return meta_tags

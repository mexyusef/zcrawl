"""
Request throttling functionality to avoid detection and respect server limitations.
"""
import time
from typing import Dict, Optional
import random
from urllib.parse import urlparse


class RequestThrottler:
    """
    Manages request timing to avoid detection and respect server limitations.
    """

    def __init__(self,
                 default_delay: float = 1.0,
                 min_delay: float = 0.5,
                 max_delay: float = 5.0,
                 jitter: float = 0.2):
        """
        Initialize the throttler.

        Args:
            default_delay: Default delay between requests in seconds
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
            jitter: Random variation factor (0-1) to add to delays
        """
        self.default_delay = default_delay
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.domain_timestamps: Dict[str, float] = {}
        self.domain_delays: Dict[str, float] = {}

    def wait(self, url: str) -> None:
        """
        Wait the appropriate amount of time before making a request to the given URL.

        Args:
            url: The URL to be requested
        """
        domain = self._get_domain(url)
        current_time = time.time()

        # Get the last access time for this domain, or 0 if it's the first time
        last_access_time = self.domain_timestamps.get(domain, 0)

        # Calculate the delay needed - use domain-specific delay if set
        delay = self.domain_delays.get(domain, self.default_delay)

        # Add random jitter
        if self.jitter > 0:
            jitter_amount = delay * self.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)

        # Ensure delay is within bounds
        delay = max(self.min_delay, min(self.max_delay, delay))

        # Calculate how much time we need to wait
        elapsed = current_time - last_access_time
        wait_time = max(0, delay - elapsed)

        if wait_time > 0:
            time.sleep(wait_time)

        # Update the timestamp for this domain
        self.domain_timestamps[domain] = time.time()

    def set_domain_delay(self, domain: str, delay: float) -> None:
        """
        Set a custom delay for a specific domain.

        Args:
            domain: The domain to set delay for
            delay: The delay in seconds
        """
        self.domain_delays[domain] = max(self.min_delay, min(self.max_delay, delay))

    def reset_domain_delay(self, domain: str) -> None:
        """
        Reset the delay for a domain to the default.

        Args:
            domain: The domain to reset
        """
        if domain in self.domain_delays:
            del self.domain_delays[domain]

    def _get_domain(self, url: str) -> str:
        """
        Extract the domain from a URL.

        Args:
            url: The URL to extract domain from

        Returns:
            The domain name
        """
        parsed = urlparse(url)
        return parsed.netloc

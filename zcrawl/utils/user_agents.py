"""
User agent management functionality.
"""
import random
from typing import List, Optional

# List of modern browser user agents
DEFAULT_USER_AGENTS = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/121.0",

    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",

    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]


class UserAgentManager:
    """Manager for handling and rotating user agents."""

    def __init__(self, user_agents: Optional[List[str]] = None):
        """
        Initialize with a list of user agents.

        Args:
            user_agents: List of user agent strings. If None, uses default list.
        """
        self.user_agents = user_agents if user_agents else DEFAULT_USER_AGENTS
        self.current_index = 0

    def get_random(self) -> str:
        """Get a random user agent from the list."""
        return random.choice(self.user_agents)

    def get_next(self) -> str:
        """Get the next user agent in rotation."""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent

    def add(self, user_agent: str) -> None:
        """
        Add a new user agent to the list.

        Args:
            user_agent: User agent string to add.
        """
        if user_agent not in self.user_agents:
            self.user_agents.append(user_agent)

    def remove(self, user_agent: str) -> bool:
        """
        Remove a user agent from the list.

        Args:
            user_agent: User agent string to remove.

        Returns:
            True if removed, False if not found.
        """
        if user_agent in self.user_agents and len(self.user_agents) > 1:
            self.user_agents.remove(user_agent)
            # Adjust current index if needed
            if self.current_index >= len(self.user_agents):
                self.current_index = 0
            return True
        return False

    def clear(self) -> None:
        """Clear all user agents."""
        self.user_agents = []
        self.current_index = 0

    def reset(self) -> None:
        """Reset to default user agents."""
        self.user_agents = DEFAULT_USER_AGENTS.copy()
        self.current_index = 0

"""
Update Checker Module
=====================

Handles version checking and update notifications for Discord bots.
Compares current version against remote version to detect available updates.

Version Format: MAJOR.MINOR.PATCH[-TYPE]
    - TYPE: dev, beta, alpha, or stable (default)
    - Examples: 1.7.2-alpha, 2.0.0, 1.5.1-beta

Features:
    - Semantic versioning support
    - GitHub integration
    - Pre-release detection
    - Automatic update notifications
    - Async operation
"""

import re
import asyncio
import aiohttp
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ReleaseType(Enum):
    """Version release types."""
    STABLE = "stable"
    BETA = "beta"
    ALPHA = "alpha"
    DEV = "dev"
    UNKNOWN = "unknown"


class UpdateCheckerConfig:
    """
    Configuration for the Update Checker.
    
    Attributes:
        GITHUB_REPO: Repository URL
        GITHUB_API: GitHub API endpoint
        VERSION_URL: Raw URL to version.txt
        TIMEOUT: Request timeout in seconds
        CHECK_INTERVAL: Auto-check interval in hours
    """
    
    GITHUB_REPO = "https://github.com/Oppro-net-Development/ManagerX"
    GITHUB_API = "https://api.github.com/repos/Oppro-net-Development/ManagerX"
    VERSION_URL = "https://raw.githubusercontent.com/Oppro-net-Development/ManagerX/main/config/version.txt"
    
    TIMEOUT = 10
    CHECK_INTERVAL = 24  # hours
    
    # Color codes for console output
    COLORS = {
        "reset": "\033[0m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "bold": "\033[1m"
    }


class VersionInfo:
    """
    Structured version information.
    
    Attributes:
        major: Major version number
        minor: Minor version number
        patch: Patch version number
        release_type: Type of release (stable, beta, etc.)
        raw: Original version string
    """
    
    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        release_type: ReleaseType = ReleaseType.STABLE,
        raw: str = ""
    ):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.release_type = release_type
        self.raw = raw or f"{major}.{minor}.{patch}"
    
    @property
    def core(self) -> Tuple[int, int, int]:
        """Get core version numbers without release type."""
        return (self.major, self.minor, self.patch)
    
    def __str__(self) -> str:
        return self.raw
    
    def __repr__(self) -> str:
        return f"VersionInfo({self.major}.{self.minor}.{self.patch}-{self.release_type.value})"
    
    def __gt__(self, other: 'VersionInfo') -> bool:
        """Compare versions (greater than)."""
        return self.core > other.core
    
    def __lt__(self, other: 'VersionInfo') -> bool:
        """Compare versions (less than)."""
        return self.core < other.core
    
    def __eq__(self, other: 'VersionInfo') -> bool:
        """Compare versions (equal)."""
        return self.core == other.core and self.release_type == other.release_type
    
    def is_stable(self) -> bool:
        """Check if this is a stable release."""
        return self.release_type == ReleaseType.STABLE
    
    def is_prerelease(self) -> bool:
        """Check if this is a pre-release version."""
        return self.release_type in (ReleaseType.ALPHA, ReleaseType.BETA, ReleaseType.DEV)


class VersionChecker:
    """
    Advanced version checker with GitHub integration.
    
    Features:
        - Semantic version parsing and comparison
        - GitHub API integration
        - Release notes fetching
        - Automatic update notifications
        - Async operations
    
    Examples:
        >>> checker = VersionChecker("1.7.2-alpha")
        >>> update_info = await checker.check_for_updates()
        >>> if update_info["update_available"]:
        ...     print(f"Update to {update_info['latest_version']}")
    """
    
    def __init__(self, current_version: str, config: Optional[UpdateCheckerConfig] = None):
        """
        Initialize version checker.
        
        Args:
            current_version: Current bot version
            config: Optional custom configuration
        """
        self.config = config or UpdateCheckerConfig()
        self.current_version = self.parse_version(current_version)
        self._last_check: Optional[datetime] = None
        self._cached_result: Optional[Dict] = None
    
    @staticmethod
    def parse_version(version_str: str) -> VersionInfo:
        """
        Parse version string into structured VersionInfo.
        
        Args:
            version_str: Version string (e.g., "1.7.2-alpha")
        
        Returns:
            VersionInfo object
        
        Examples:
            >>> info = VersionChecker.parse_version("1.7.2-alpha")
            >>> print(f"{info.major}.{info.minor}.{info.patch}")
            1.7.2
        """
        pattern = r"(\d+)\.(\d+)\.(\d+)(?:[-_]?(dev|beta|alpha))?"
        match = re.match(pattern, version_str.lower())
        
        if not match:
            logger.warning(f"Invalid version format: {version_str}")
            return VersionInfo(0, 0, 0, ReleaseType.UNKNOWN, version_str)
        
        major, minor, patch, type_str = match.groups()
        
        # Parse release type
        release_type = ReleaseType.STABLE
        if type_str:
            try:
                release_type = ReleaseType(type_str)
            except ValueError:
                release_type = ReleaseType.UNKNOWN
        
        return VersionInfo(
            int(major),
            int(minor),
            int(patch),
            release_type,
            version_str
        )
    
    async def fetch_latest_version(self) -> Optional[VersionInfo]:
        """
        Fetch latest version from remote.
        
        Returns:
            VersionInfo of latest version or None on error
        """
        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
                async with session.get(self.config.VERSION_URL, timeout=timeout) as resp:
                    if resp.status != 200:
                        logger.error(f"Version check failed: HTTP {resp.status}")
                        return None
                    
                    version_text = (await resp.text()).strip()
                    if not version_text:
                        logger.error("Empty version response")
                        return None
                    
                    return self.parse_version(version_text)
        
        except aiohttp.ClientConnectorError:
            logger.error("Could not connect to GitHub (network issue)")
        except asyncio.TimeoutError:
            logger.error("Version check timed out")
        except Exception as e:
            logger.error(f"Unexpected error fetching version: {e}")
        
        return None
    
    async def fetch_release_notes(self, version: str) -> Optional[str]:
        """
        Fetch release notes from GitHub.
        
        Args:
            version: Version tag to fetch notes for
        
        Returns:
            Release notes text or None
        """
        try:
            url = f"{self.config.GITHUB_API}/releases/tags/v{version}"
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self.config.TIMEOUT)
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status != 200:
                        return None
                    
                    data = await resp.json()
                    return data.get("body", "No release notes available.")
        
        except Exception as e:
            logger.debug(f"Could not fetch release notes: {e}")
            return None
    
    async def check_for_updates(self, force: bool = False) -> Dict[str, Any]:
        """
        Check for available updates.
        
        Args:
            force: Force check even if cached result exists
        
        Returns:
            Dictionary with update information:
                - update_available: bool
                - current_version: str
                - latest_version: str
                - is_prerelease: bool
                - is_dev_build: bool
                - release_notes: Optional[str]
                - download_url: str
        
        Examples:
            >>> info = await checker.check_for_updates()
            >>> if info["update_available"]:
            ...     print(f"New version: {info['latest_version']}")
        """
        # Return cached result if recent
        if not force and self._cached_result and self._last_check:
            time_since_check = (datetime.now() - self._last_check).total_seconds() / 3600
            if time_since_check < self.config.CHECK_INTERVAL:
                return self._cached_result
        
        latest = await self.fetch_latest_version()
        
        if not latest:
            return {
                "update_available": False,
                "current_version": str(self.current_version),
                "latest_version": None,
                "error": "Could not fetch latest version"
            }
        
        # Compare versions
        update_available = False
        is_dev_build = False
        is_prerelease = False
        
        if self.current_version > latest:
            is_dev_build = True
        elif self.current_version < latest:
            update_available = True
        elif self.current_version.is_prerelease() and latest.is_stable():
            is_prerelease = True
        
        # Fetch release notes if update available
        release_notes = None
        if update_available:
            release_notes = await self.fetch_release_notes(str(latest))
        
        result = {
            "update_available": update_available,
            "current_version": str(self.current_version),
            "latest_version": str(latest),
            "is_prerelease": is_prerelease,
            "is_dev_build": is_dev_build,
            "release_notes": release_notes,
            "download_url": self.config.GITHUB_REPO
        }
        
        # Cache result
        self._cached_result = result
        self._last_check = datetime.now()
        
        return result
    
    async def print_update_status(self) -> None:
        """
        Print formatted update status to console.
        
        Shows colored output with update information.
        """
        info = await self.check_for_updates()
        colors = self.config.COLORS
        
        if info.get("error"):
            print(f"{colors['red']}[UPDATE CHECK FAILED]{colors['reset']} {info['error']}")
            return
        
        current = info["current_version"]
        latest = info["latest_version"]
        
        if info["update_available"]:
            print(f"\n{colors['yellow']}{colors['bold']}[UPDATE AVAILABLE]{colors['reset']}")
            print(f"  Current: {colors['red']}{current}{colors['reset']}")
            print(f"  Latest:  {colors['green']}{latest}{colors['reset']}")
            print(f"  Download: {colors['cyan']}{info['download_url']}{colors['reset']}\n")
            
            if info["release_notes"]:
                print(f"{colors['bold']}Release Notes:{colors['reset']}")
                print(f"{info['release_notes'][:200]}...")
        
        elif info["is_dev_build"]:
            print(f"{colors['cyan']}[DEV BUILD]{colors['reset']} "
                  f"Running {current} (newer than public {latest})")
        
        elif info["is_prerelease"]:
            print(f"{colors['yellow']}[PRE-RELEASE]{colors['reset']} "
                  f"Running {current} (latest stable: {latest})")
        
        else:
            print(f"{colors['green']}[UP TO DATE]{colors['reset']} "
                  f"Running latest version: {current}")
    
    def get_version_info(self) -> Dict[str, Any]:
        """
        Get detailed information about current version.
        
        Returns:
            Dictionary with version details
        """
        return {
            "version": str(self.current_version),
            "major": self.current_version.major,
            "minor": self.current_version.minor,
            "patch": self.current_version.patch,
            "release_type": self.current_version.release_type.value,
            "is_stable": self.current_version.is_stable(),
            "is_prerelease": self.current_version.is_prerelease()
        }

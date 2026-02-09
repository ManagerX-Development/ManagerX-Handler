"""
Update Checker Module - Extended Edition
=========================================

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
    - Configurable settings
    - Colored logging with colorama
"""

import re
import asyncio
import aiohttp
from typing import Optional, Tuple, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path
import logging

try:
    from colorama import Fore, Style, init as colorama_init
    COLORAMA_AVAILABLE = True
    colorama_init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback to empty strings if colorama not available
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
    
    class Style:
        RESET_ALL = ""
        BRIGHT = ""
        DIM = ""

logger = logging.getLogger(__name__)


class ReleaseType(Enum):
    """Version release types."""
    STABLE = "stable"
    BETA = "beta"
    ALPHA = "alpha"
    DEV = "dev"
    UNKNOWN = "unknown"


class UpdateCheckerSettings:
    """
    Global settings for Update Checker.
    
    Configure once at application startup and settings persist
    throughout the project lifecycle.
    """
    
    # Default GitHub repository settings
    github_repo: str = "https://github.com/Oppro-net-Development/ManagerX"
    github_api: str = "https://api.github.com/repos/Oppro-net-Development/ManagerX"
    version_url: str = "https://raw.githubusercontent.com/Oppro-net-Development/ManagerX/main/config/version.txt"
    
    # Version file settings
    version_file_path: Optional[Path] = None
    auto_read_version: bool = True
    
    # Network settings
    timeout: int = 10
    check_interval: int = 24  # hours
    
    # Logging settings
    logging_enabled: bool = True
    colored_logging: bool = True
    log_level: str = "INFO"
    
    # Notification settings
    show_console_updates: bool = True
    auto_check_on_start: bool = True
    notify_dev_builds: bool = True
    notify_prereleases: bool = True
    
    _configured: bool = False
    
    @classmethod
    def configure(
        cls,
        github_repo: Optional[str] = None,
        version_url: Optional[str] = None,
        version_file: Optional[str] = None,
        timeout: Optional[int] = None,
        check_interval: Optional[int] = None,
        logging: bool = True,
        colored: bool = True,
        log_level: str = "INFO",
        auto_check: bool = True,
        show_console: bool = True
    ) -> None:
        """
        Configure global update checker settings.
        
        Args:
            github_repo: GitHub repository URL
            version_url: URL to raw version.txt file
            version_file: Path to local version.txt file
            timeout: Request timeout in seconds
            check_interval: Auto-check interval in hours
            logging: Enable/disable update checker logging
            colored: Enable/disable colored console output
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            auto_check: Auto-check for updates on initialization
            show_console: Show update notifications in console
        
        Examples:
            >>> UpdateCheckerSettings.configure(
            ...     github_repo="https://github.com/user/repo",
            ...     version_file="config/version.txt",
            ...     logging=True,
            ...     colored=True
            ... )
        """
        if github_repo is not None:
            cls.github_repo = github_repo
            # Auto-generate API URL
            repo_path = github_repo.replace("https://github.com/", "")
            cls.github_api = f"https://api.github.com/repos/{repo_path}"
        
        if version_url is not None:
            cls.version_url = version_url
        
        if version_file is not None:
            cls.version_file_path = Path(version_file)
            cls.auto_read_version = True
        
        if timeout is not None:
            cls.timeout = timeout
        
        if check_interval is not None:
            cls.check_interval = check_interval
        
        cls.logging_enabled = logging
        cls.colored_logging = colored and COLORAMA_AVAILABLE
        cls.log_level = log_level.upper()
        cls.auto_check_on_start = auto_check
        cls.show_console_updates = show_console
        
        cls._configured = True
        
        # Log configuration
        if cls.logging_enabled:
            cls._log_info(
                f"UpdateChecker configured: repo={cls.github_repo.split('/')[-1]}, "
                f"interval={cls.check_interval}h, "
                f"auto_check={cls.auto_check_on_start}"
            )
    
    @classmethod
    def _log(cls, level: str, message: str, color: str = "") -> None:
        """Internal logging method with optional coloring."""
        if not cls.logging_enabled:
            return
        
        prefix = f"{color}[UPDATE]{Style.RESET_ALL}" if cls.colored_logging else "[UPDATE]"
        full_message = f"{prefix} {message}"
        
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(full_message)
        
        # Also print to console for visibility
        if cls.show_console_updates or level.lower() in ["warning", "error"]:
            print(full_message)
    
    @classmethod
    def _log_debug(cls, message: str) -> None:
        """Log debug message."""
        if cls.log_level == "DEBUG":
            cls._log("debug", message, Fore.CYAN)
    
    @classmethod
    def _log_info(cls, message: str) -> None:
        """Log info message."""
        if cls.log_level in ["DEBUG", "INFO"]:
            cls._log("info", message, Fore.BLUE)
    
    @classmethod
    def _log_warning(cls, message: str) -> None:
        """Log warning message."""
        if cls.log_level in ["DEBUG", "INFO", "WARNING"]:
            cls._log("warning", message, Fore.YELLOW)
    
    @classmethod
    def _log_error(cls, message: str) -> None:
        """Log error message."""
        cls._log("error", message, Fore.RED)
    
    @classmethod
    def _log_success(cls, message: str) -> None:
        """Log success message."""
        if cls.log_level in ["DEBUG", "INFO"]:
            color = f"{Fore.GREEN}{Style.BRIGHT}" if cls.colored_logging else ""
            cls._log("info", message, color)
    
    @classmethod
    def _log_update_available(cls, current: str, latest: str) -> None:
        """Log update available message."""
        if cls.log_level in ["DEBUG", "INFO"]:
            color = f"{Fore.YELLOW}{Style.BRIGHT}" if cls.colored_logging else ""
            cls._log("info", f"Update available: {current} → {latest}", color)


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
        - Configurable settings
        - Colored console output
    
    Examples:
        >>> # Configure once at startup
        >>> VersionChecker.settings(
        ...     github_repo="https://github.com/user/repo",
        ...     version_file="config/version.txt",
        ...     logging=True,
        ...     colored=True
        ... )
        >>> 
        >>> # Use throughout the project
        >>> checker = VersionChecker("1.7.2-alpha")
        >>> update_info = await checker.check_for_updates()
        >>> if update_info["update_available"]:
        ...     print(f"Update to {update_info['latest_version']}")
    """
    
    _settings = UpdateCheckerSettings
    
    def __init__(self, current_version: Optional[str] = None):
        """
        Initialize version checker.
        
        Args:
            current_version: Current bot version (auto-read from file if not provided)
        """
        # Auto-read version from file if configured
        if current_version is None and self._settings.auto_read_version:
            current_version = self._read_version_file()
        
        if current_version is None:
            raise ValueError(
                "No version provided and auto-read failed. "
                "Either provide version or configure version_file in settings."
            )
        
        self.current_version = self.parse_version(current_version)
        self._last_check: Optional[datetime] = None
        self._cached_result: Optional[Dict] = None
        
        # Log initialization
        self._settings._log_debug(
            f"VersionChecker initialized with version {self.current_version}"
        )
        
        # Auto-check on start if configured
        if self._settings.auto_check_on_start:
            asyncio.create_task(self._auto_check_on_init())
    
    def _read_version_file(self) -> Optional[str]:
        """Read version from configured file."""
        if not self._settings.version_file_path:
            return None
        
        try:
            version_file = Path(self._settings.version_file_path)
            if not version_file.exists():
                self._settings._log_warning(
                    f"Version file not found: {version_file}"
                )
                return None
            
            version = version_file.read_text(encoding="utf-8").strip()
            self._settings._log_debug(f"Read version from file: {version}")
            return version
        
        except Exception as e:
            self._settings._log_error(f"Error reading version file: {e}")
            return None
    
    async def _auto_check_on_init(self) -> None:
        """Auto-check for updates on initialization."""
        try:
            await asyncio.sleep(2)  # Small delay to not block startup
            await self.check_for_updates()
        except Exception as e:
            self._settings._log_debug(f"Auto-check failed: {e}")
    
    @classmethod
    def settings(
        cls,
        github_repo: Optional[str] = None,
        version_url: Optional[str] = None,
        version_file: Optional[str] = None,
        timeout: Optional[int] = None,
        check_interval: Optional[int] = None,
        logging: bool = True,
        colored: bool = True,
        log_level: str = "INFO",
        auto_check: bool = True,
        show_console: bool = True
    ) -> None:
        """
        Configure VersionChecker settings.
        
        Call this once at application startup. Settings persist for
        the entire project lifecycle.
        
        Args:
            github_repo: GitHub repository URL
            version_url: URL to raw version.txt file
            version_file: Path to local version.txt (default: "config/version.txt")
            timeout: Request timeout in seconds (default: 10)
            check_interval: Auto-check interval in hours (default: 24)
            logging: Enable update checker logging (default: True)
            colored: Enable colored console output (default: True)
            log_level: Log level - DEBUG, INFO, WARNING, ERROR (default: INFO)
            auto_check: Auto-check for updates on start (default: True)
            show_console: Show update notifications (default: True)
        
        Examples:
            >>> VersionChecker.settings(
            ...     github_repo="https://github.com/user/bot",
            ...     version_file="config/version.txt",
            ...     logging=True,
            ...     colored=True,
            ...     log_level="INFO"
            ... )
        """
        cls._settings.configure(
            github_repo=github_repo,
            version_url=version_url,
            version_file=version_file,
            timeout=timeout,
            check_interval=check_interval,
            logging=logging,
            colored=colored,
            log_level=log_level,
            auto_check=auto_check,
            show_console=show_console
        )
    
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
            UpdateCheckerSettings._log_warning(f"Invalid version format: {version_str}")
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
        self._settings._log_debug(f"Fetching latest version from {self._settings.version_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self._settings.timeout)
                async with session.get(self._settings.version_url, timeout=timeout) as resp:
                    if resp.status != 200:
                        self._settings._log_error(
                            f"Version check failed: HTTP {resp.status}"
                        )
                        return None
                    
                    version_text = (await resp.text()).strip()
                    if not version_text:
                        self._settings._log_error("Empty version response")
                        return None
                    
                    version = self.parse_version(version_text)
                    self._settings._log_success(f"Latest version fetched: {version}")
                    return version
        
        except aiohttp.ClientConnectorError:
            self._settings._log_error("Could not connect to GitHub (network issue)")
        except asyncio.TimeoutError:
            self._settings._log_error(
                f"Version check timed out after {self._settings.timeout}s"
            )
        except Exception as e:
            self._settings._log_error(f"Unexpected error fetching version: {e}")
        
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
            url = f"{self._settings.github_api}/releases/tags/v{version}"
            self._settings._log_debug(f"Fetching release notes from {url}")
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=self._settings.timeout)
                async with session.get(url, timeout=timeout) as resp:
                    if resp.status != 200:
                        self._settings._log_debug(
                            f"Release notes not found (HTTP {resp.status})"
                        )
                        return None
                    
                    data = await resp.json()
                    notes = data.get("body", "No release notes available.")
                    self._settings._log_debug("Release notes fetched successfully")
                    return notes
        
        except Exception as e:
            self._settings._log_debug(f"Could not fetch release notes: {e}")
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
        self._settings._log_debug("Checking for updates...")
        
        # Return cached result if recent
        if not force and self._cached_result and self._last_check:
            time_since_check = (datetime.now() - self._last_check).total_seconds() / 3600
            if time_since_check < self._settings.check_interval:
                self._settings._log_debug(
                    f"Using cached result (checked {time_since_check:.1f}h ago)"
                )
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
            if self._settings.notify_dev_builds:
                self._settings._log_info(
                    f"Running dev build: {self.current_version} > {latest}"
                )
        elif self.current_version < latest:
            update_available = True
            self._settings._log_update_available(
                str(self.current_version),
                str(latest)
            )
        elif self.current_version.is_prerelease() and latest.is_stable():
            is_prerelease = True
            if self._settings.notify_prereleases:
                self._settings._log_info(
                    f"Running pre-release: {self.current_version} (stable: {latest})"
                )
        else:
            self._settings._log_success(
                f"Up to date: {self.current_version}"
            )
        
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
            "download_url": self._settings.github_repo
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
        
        if not self._settings.show_console_updates:
            return
        
        if info.get("error"):
            color = f"{Fore.RED}{Style.BRIGHT}" if self._settings.colored_logging else ""
            reset = Style.RESET_ALL if self._settings.colored_logging else ""
            print(f"\n{color}[UPDATE CHECK FAILED]{reset} {info['error']}\n")
            return
        
        current = info["current_version"]
        latest = info["latest_version"]
        
        if self._settings.colored_logging:
            self._print_colored_status(info, current, latest)
        else:
            self._print_plain_status(info, current, latest)
    
    def _print_colored_status(self, info: Dict, current: str, latest: str) -> None:
        """Print colored update status."""
        if info["update_available"]:
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}╔══════════════════════════════════════╗{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}║     UPDATE AVAILABLE                 ║{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}╚══════════════════════════════════════╝{Style.RESET_ALL}")
            print(f"  Current: {Fore.RED}{current}{Style.RESET_ALL}")
            print(f"  Latest:  {Fore.GREEN}{Style.BRIGHT}{latest}{Style.RESET_ALL}")
            print(f"  Download: {Fore.CYAN}{info['download_url']}{Style.RESET_ALL}\n")
            
            if info["release_notes"]:
                print(f"{Style.BRIGHT}Release Notes:{Style.RESET_ALL}")
                notes = info['release_notes'][:300]
                print(f"{Fore.WHITE}{notes}...{Style.RESET_ALL}\n")
        
        elif info["is_dev_build"]:
            print(f"\n{Fore.CYAN}{Style.BRIGHT}[DEV BUILD]{Style.RESET_ALL} "
                  f"Running {Fore.CYAN}{current}{Style.RESET_ALL} "
                  f"(newer than public {Fore.YELLOW}{latest}{Style.RESET_ALL})\n")
        
        elif info["is_prerelease"]:
            print(f"\n{Fore.YELLOW}[PRE-RELEASE]{Style.RESET_ALL} "
                  f"Running {Fore.YELLOW}{current}{Style.RESET_ALL} "
                  f"(latest stable: {Fore.GREEN}{latest}{Style.RESET_ALL})\n")
        
        else:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ UP TO DATE{Style.RESET_ALL} "
                  f"Running latest version: {Fore.GREEN}{current}{Style.RESET_ALL}\n")
    
    def _print_plain_status(self, info: Dict, current: str, latest: str) -> None:
        """Print plain text update status (no colors)."""
        if info["update_available"]:
            print("\n" + "="*40)
            print("UPDATE AVAILABLE")
            print("="*40)
            print(f"  Current: {current}")
            print(f"  Latest:  {latest}")
            print(f"  Download: {info['download_url']}\n")
            
            if info["release_notes"]:
                print("Release Notes:")
                print(info['release_notes'][:300] + "...\n")
        
        elif info["is_dev_build"]:
            print(f"\n[DEV BUILD] Running {current} (newer than public {latest})\n")
        
        elif info["is_prerelease"]:
            print(f"\n[PRE-RELEASE] Running {current} (latest stable: {latest})\n")
        
        else:
            print(f"\n[UP TO DATE] Running latest version: {current}\n")
    
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
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """
        Get current configuration settings.
        
        Returns:
            Dictionary with all current settings
        """
        return {
            "github_repo": cls._settings.github_repo,
            "github_api": cls._settings.github_api,
            "version_url": cls._settings.version_url,
            "version_file_path": str(cls._settings.version_file_path) if cls._settings.version_file_path else None,
            "timeout": cls._settings.timeout,
            "check_interval": cls._settings.check_interval,
            "logging_enabled": cls._settings.logging_enabled,
            "colored_logging": cls._settings.colored_logging,
            "log_level": cls._settings.log_level,
            "auto_check_on_start": cls._settings.auto_check_on_start,
            "show_console_updates": cls._settings.show_console_updates,
            "configured": cls._settings._configured,
            "colorama_available": COLORAMA_AVAILABLE
        }
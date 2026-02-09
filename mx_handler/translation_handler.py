"""
Translation Handler Module
==========================

Provides centralized translation management with caching, fallback languages,
and async support for Discord bots.

Features:
    - YAML-based translations
    - Multi-level fallback system
    - Automatic caching with TTL
    - User-specific language detection
    - Placeholder formatting with validation
    - Hot-reload support
    - Configurable paths and logging
    - Colored console output
"""

import asyncio
import yaml
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from datetime import datetime, timedelta
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

logger = logging.getLogger(__name__)


class TranslationSettings:
    """
    Global settings for TranslationHandler.
    
    Configure once at application startup and settings persist
    throughout the project lifecycle.
    """
    
    # Default settings
    translation_path: Path = Path("translation") / "messages"
    fallback_languages: tuple = ("en", "de")
    default_language: str = "en"
    cache_ttl_minutes: int = 30
    logging_enabled: bool = True
    colored_logging: bool = True
    log_level: str = "INFO"
    
    _configured: bool = False
    
    @classmethod
    def configure(
        cls,
        path: Optional[Union[str, Path]] = None,
        fallback_langs: Optional[tuple] = None,
        default_lang: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        logging: bool = True,
        colored: bool = True,
        log_level: str = "INFO"
    ) -> None:
        """
        Configure global translation settings.
        
        Args:
            path: Path to translation files directory
            fallback_langs: Tuple of fallback language codes
            default_lang: Default language code
            cache_ttl: Cache TTL in minutes
            logging: Enable/disable translation logging
            colored: Enable/disable colored console output
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
        Examples:
            >>> TranslationSettings.configure(
            ...     path="locales/messages",
            ...     logging=True,
            ...     colored=True
            ... )
        """
        if path is not None:
            cls.translation_path = Path(path)
        
        if fallback_langs is not None:
            cls.fallback_languages = fallback_langs
        
        if default_lang is not None:
            cls.default_language = default_lang
        
        if cache_ttl is not None:
            cls.cache_ttl_minutes = cache_ttl
        
        cls.logging_enabled = logging
        cls.colored_logging = colored and COLORAMA_AVAILABLE
        cls.log_level = log_level.upper()
        
        cls._configured = True
        
        # Log configuration
        if cls.logging_enabled:
            cls._log_info(
                f"TranslationHandler configured: path={cls.translation_path}, "
                f"default={cls.default_language}, "
                f"fallbacks={cls.fallback_languages}"
            )
    
    @classmethod
    def _log(cls, level: str, message: str, color: str = "") -> None:
        """Internal logging method with optional coloring."""
        if not cls.logging_enabled:
            return
        
        prefix = f"{color}[TRANSLATION]{Style.RESET_ALL}" if cls.colored_logging else "[TRANSLATION]"
        full_message = f"{prefix} {message}"
        
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(full_message)
        
        # Also print to console for visibility
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
            cls._log("info", message, Fore.GREEN)
    
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


class TranslationCache:
    """
    Advanced caching system for translations with TTL support.
    
    Features:
        - Time-based expiration
        - Memory usage tracking
        - Automatic cleanup
    """
    
    def __init__(self, ttl_minutes: int = 30):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
        self._lock = asyncio.Lock()
    
    def update_ttl(self, ttl_minutes: int) -> None:
        """Update cache TTL setting."""
        self._ttl = timedelta(minutes=ttl_minutes)
    
    async def get(self, key: str) -> Optional[Dict]:
        """Get cached translation data if valid."""
        async with self._lock:
            if key not in self._cache:
                return None
            
            if datetime.now() - self._timestamps[key] > self._ttl:
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            return self._cache[key]
    
    async def set(self, key: str, value: Dict) -> None:
        """Store translation data in cache."""
        async with self._lock:
            self._cache[key] = value
            self._timestamps[key] = datetime.now()
    
    async def clear(self, key: Optional[str] = None) -> None:
        """Clear cache entry or entire cache."""
        async with self._lock:
            if key:
                self._cache.pop(key, None)
                self._timestamps.pop(key, None)
            else:
                self._cache.clear()
                self._timestamps.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "languages": list(self._cache.keys()),
            "oldest_entry": min(self._timestamps.values()) if self._timestamps else None
        }


class TranslationHandler:
    """
    Central translation management system.
    
    Supports:
        - Multi-language YAML files
        - Cascading fallback system
        - User-specific translations
        - Nested key paths (dot notation)
        - Dynamic placeholder replacement
        - Async operations
        - Configurable paths and settings
        - Colored logging output
    
    Examples:
        >>> # Configure once at startup
        >>> TranslationHandler.settings(
        ...     path="locales/messages",
        ...     logging=True,
        ...     colored=True
        ... )
        >>> 
        >>> # Use throughout the project
        >>> handler = TranslationHandler()
        >>> text = handler.get("de", "welcome.title", user="Alice")
        >>> text = await handler.get_for_user(bot, 123456, "error.not_found")
    """
    
    _settings = TranslationSettings
    _cache: Optional[TranslationCache] = None
    _file_watchers: Dict[str, float] = {}
    
    @classmethod
    def settings(
        cls,
        path: Optional[Union[str, Path]] = None,
        fallback_langs: Optional[tuple] = None,
        default_lang: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        logging: bool = True,
        colored: bool = True,
        log_level: str = "INFO"
    ) -> None:
        """
        Configure TranslationHandler settings.
        
        Call this once at application startup. Settings persist for
        the entire project lifecycle.
        
        Args:
            path: Path to translation files (default: "translation/messages")
            fallback_langs: Fallback languages tuple (default: ("en", "de"))
            default_lang: Default language code (default: "en")
            cache_ttl: Cache time-to-live in minutes (default: 30)
            logging: Enable translation logging (default: True)
            colored: Enable colored console output (default: True)
            log_level: Log level - DEBUG, INFO, WARNING, ERROR (default: INFO)
        
        Examples:
            >>> TranslationHandler.settings(
            ...     path="locales",
            ...     logging=True,
            ...     colored=True,
            ...     log_level="DEBUG"
            ... )
        """
        cls._settings.configure(
            path=path,
            fallback_langs=fallback_langs,
            default_lang=default_lang,
            cache_ttl=cache_ttl,
            logging=logging,
            colored=colored,
            log_level=log_level
        )
        
        # Reinitialize cache with new TTL
        if cls._cache is None or (cache_ttl is not None):
            ttl = cache_ttl if cache_ttl is not None else cls._settings.cache_ttl_minutes
            cls._cache = TranslationCache(ttl_minutes=ttl)
        elif cls._cache is not None and cache_ttl is not None:
            cls._cache.update_ttl(cache_ttl)
    
    @classmethod
    def _ensure_cache(cls) -> None:
        """Ensure cache is initialized."""
        if cls._cache is None:
            cls._cache = TranslationCache(ttl_minutes=cls._settings.cache_ttl_minutes)
    
    @classmethod
    async def load_messages(cls, lang_code: str, force_reload: bool = False) -> Dict:
        """
        Load language files with caching and fallback.
        
        Args:
            lang_code: Language code (e.g., 'en', 'de', 'es')
            force_reload: Bypass cache and reload from disk
        
        Returns:
            Dictionary containing all translations for the language
        
        Raises:
            FileNotFoundError: If no valid translation file exists
        """
        cls._ensure_cache()
        
        # Check cache first
        if not force_reload:
            cached = await cls._cache.get(lang_code)
            if cached is not None:
                cls._settings._log_debug(f"Loaded {lang_code}.yaml from cache")
                return cached
        
        # Try loading with fallback chain
        for code in (lang_code, *cls._settings.fallback_languages):
            file_path = cls._settings.translation_path / f"{code}.yaml"
            
            if not file_path.exists():
                cls._settings._log_debug(f"File not found: {file_path}")
                continue
            
            try:
                # Check if file was modified
                mtime = file_path.stat().st_mtime
                if code in cls._file_watchers and cls._file_watchers[code] == mtime and not force_reload:
                    cached = await cls._cache.get(code)
                    if cached:
                        cls._settings._log_debug(f"Loaded {code}.yaml from cache (unchanged)")
                        return cached
                
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                
                # Validate structure
                if not isinstance(data, dict):
                    cls._settings._log_warning(f"Invalid YAML structure in {code}.yaml")
                    continue
                
                # Cache and return
                await cls._cache.set(lang_code, data)
                cls._file_watchers[code] = mtime
                
                # Log success
                if code != lang_code:
                    cls._settings._log_info(
                        f"{code}.yaml loaded (fallback for {lang_code})"
                    )
                else:
                    cls._settings._log_success(f"{code}.yaml has loaded")
                
                return data
            
            except yaml.YAMLError as e:
                cls._settings._log_error(f"YAML parsing error in {code}.yaml: {e}")
                continue
            except Exception as e:
                cls._settings._log_error(f"Error loading {code}.yaml: {e}")
                continue
        
        # No valid translation found
        cls._settings._log_warning(
            f"No translation file found for '{lang_code}' or fallbacks"
        )
        await cls._cache.set(lang_code, {})
        return {}
    
    @classmethod
    def get(
        cls,
        lang_code: str,
        path: Union[str, List[str]],
        default: str = "",
        **placeholders
    ) -> str:
        """
        Get translation for a specific path with placeholder replacement.
        
        Args:
            lang_code: Language code
            path: Translation key path (dot-separated string or list)
            default: Fallback value if key not found
            **placeholders: Variables to replace in translation
        
        Returns:
            Translated and formatted string
        
        Examples:
            >>> get("en", "welcome.title", user="Alice")
            "Welcome, Alice!"
            
            >>> get("de", ["error", "invalid_input"], field="Email")
            "Ungültige Eingabe: Email"
        """
        # Parse path
        if isinstance(path, str):
            path = path.split(".")
        
        # Load messages (sync wrapper for backward compatibility)
        try:
            loop = asyncio.get_event_loop()
            messages = loop.run_until_complete(cls.load_messages(lang_code))
        except RuntimeError:
            # No event loop - create temporary one
            messages = asyncio.run(cls.load_messages(lang_code))
        
        # Navigate through nested structure
        value = messages
        for key in path:
            if not isinstance(value, dict):
                cls._settings._log_debug(
                    f"Invalid path structure at '{key}' in {'.'.join(path)}"
                )
                return default
            value = value.get(key)
            if value is None:
                cls._settings._log_debug(f"Key not found: {'.'.join(path)}")
                return default
        
        # Ensure final value is string
        if not isinstance(value, str):
            cls._settings._log_warning(
                f"Translation at {'.'.join(path)} is not a string"
            )
            return default
        
        # Format placeholders
        try:
            return value.format(**placeholders)
        except KeyError as e:
            cls._settings._log_warning(f"Missing placeholder in translation: {e}")
            return value
        except Exception as e:
            cls._settings._log_error(f"Error formatting translation: {e}")
            return value
    
    @classmethod
    async def get_async(
        cls,
        lang_code: str,
        path: Union[str, List[str]],
        default: str = "",
        **placeholders
    ) -> str:
        """
        Async version of get() for better performance in async contexts.
        
        Args:
            lang_code: Language code
            path: Translation key path
            default: Fallback value
            **placeholders: Formatting variables
        
        Returns:
            Translated string
        """
        if isinstance(path, str):
            path = path.split(".")
        
        messages = await cls.load_messages(lang_code)
        value = messages
        
        for key in path:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        
        if not isinstance(value, str):
            return default
        
        try:
            return value.format(**placeholders)
        except Exception as e:
            cls._settings._log_error(f"Error formatting translation: {e}")
            return value
    
    @classmethod
    async def get_for_user(
        cls,
        bot: Any,
        user_id: int,
        path: Union[str, List[str]],
        default: str = "",
        **placeholders
    ) -> str:
        """
        Get translation automatically for a specific user.
        
        Detects user's preferred language from database and returns
        appropriate translation.
        
        Args:
            bot: Discord bot instance (must have settings_db)
            user_id: Discord user ID
            path: Translation key path
            default: Fallback value
            **placeholders: Formatting variables
        
        Returns:
            Translated string in user's language
        
        Examples:
            >>> await get_for_user(bot, ctx.author.id, "error.cooldown", seconds=30)
        """
        lang = cls._settings.default_language
        
        # Try to get user's language preference
        try:
            if hasattr(bot, 'settings_db'):
                user_lang = bot.settings_db.get_user_language(user_id)
                if user_lang:
                    lang = user_lang
        except Exception as e:
            cls._settings._log_debug(f"Could not fetch user language: {e}")
        
        return await cls.get_async(lang, path, default, **placeholders)
    
    @classmethod
    async def get_for_guild(
        cls,
        bot: Any,
        guild_id: int,
        path: Union[str, List[str]],
        default: str = "",
        **placeholders
    ) -> str:
        """
        Get translation for a guild's configured language.
        
        Args:
            bot: Discord bot instance
            guild_id: Discord guild ID
            path: Translation key path
            default: Fallback value
            **placeholders: Formatting variables
        
        Returns:
            Translated string in guild's language
        """
        lang = cls._settings.default_language
        
        try:
            if hasattr(bot, 'settings_db'):
                guild_lang = bot.settings_db.get_guild_language(guild_id)
                if guild_lang:
                    lang = guild_lang
        except Exception as e:
            cls._settings._log_debug(f"Could not fetch guild language: {e}")
        
        return await cls.get_async(lang, path, default, **placeholders)
    
    @classmethod
    async def get_all_translations(
        cls,
        path: Union[str, List[str]],
        languages: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """
        Get translations for a key in multiple languages.
        
        Useful for creating language selection menus.
        
        Args:
            path: Translation key path
            languages: List of language codes (default: all available)
        
        Returns:
            Dictionary mapping language codes to translated strings
        
        Examples:
            >>> translations = await get_all_translations("settings.language_name")
            >>> # {'en': 'English', 'de': 'Deutsch', 'es': 'Español'}
        """
        if languages is None:
            languages = cls.get_available_languages()
        
        results = {}
        for lang in languages:
            try:
                translation = await cls.get_async(lang, path)
                if translation:
                    results[lang] = translation
            except Exception as e:
                cls._settings._log_debug(f"Error loading translation for {lang}: {e}")
        
        return results
    
    @classmethod
    def get_available_languages(cls) -> List[str]:
        """
        Get list of all available language codes.
        
        Returns:
            List of language codes (e.g., ['en', 'de', 'es'])
        """
        if not cls._settings.translation_path.exists():
            return [cls._settings.default_language]
        
        languages = []
        for file in cls._settings.translation_path.glob("*.yaml"):
            lang_code = file.stem
            if lang_code and len(lang_code) == 2:
                languages.append(lang_code)
        
        return sorted(languages)
    
    @classmethod
    async def validate_translations(cls, lang_code: str) -> Dict[str, Any]:
        """
        Validate translation file for completeness and errors.
        
        Args:
            lang_code: Language code to validate
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "missing_keys": [],
            "extra_keys": []
        }
        
        try:
            translations = await cls.load_messages(lang_code, force_reload=True)
            
            if not translations:
                results["valid"] = False
                results["errors"].append(f"No translations found for '{lang_code}'")
                return results
            
            # Compare with default language
            if lang_code != cls._settings.default_language:
                default_trans = await cls.load_messages(cls._settings.default_language)
                
                def get_all_keys(d: Dict, prefix: str = "") -> set:
                    keys = set()
                    for k, v in d.items():
                        full_key = f"{prefix}.{k}" if prefix else k
                        if isinstance(v, dict):
                            keys.update(get_all_keys(v, full_key))
                        else:
                            keys.add(full_key)
                    return keys
                
                default_keys = get_all_keys(default_trans)
                current_keys = get_all_keys(translations)
                
                results["missing_keys"] = list(default_keys - current_keys)
                results["extra_keys"] = list(current_keys - default_keys)
                
                if results["missing_keys"]:
                    results["warnings"].append(
                        f"{len(results['missing_keys'])} keys missing compared to "
                        f"{cls._settings.default_language}"
                    )
        
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Validation error: {str(e)}")
        
        return results
    
    @classmethod
    async def clear_cache(cls, lang_code: Optional[str] = None) -> None:
        """
        Clear translation cache.
        
        Args:
            lang_code: Specific language to clear (None = clear all)
        """
        cls._ensure_cache()
        await cls._cache.clear(lang_code)
        if lang_code:
            cls._file_watchers.pop(lang_code, None)
            cls._settings._log_info(f"Cache cleared for: {lang_code}")
        else:
            cls._file_watchers.clear()
            cls._settings._log_info("Cache cleared for all languages")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get current cache statistics."""
        cls._ensure_cache()
        return cls._cache.get_stats()
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """
        Get current configuration settings.
        
        Returns:
            Dictionary with all current settings
        """
        return {
            "translation_path": str(cls._settings.translation_path),
            "fallback_languages": cls._settings.fallback_languages,
            "default_language": cls._settings.default_language,
            "cache_ttl_minutes": cls._settings.cache_ttl_minutes,
            "logging_enabled": cls._settings.logging_enabled,
            "colored_logging": cls._settings.colored_logging,
            "log_level": cls._settings.log_level,
            "configured": cls._settings._configured,
            "colorama_available": COLORAMA_AVAILABLE
        }


# Aliases for backward compatibility
MessagesHandler = TranslationHandler
LangHandler = TranslationHandler
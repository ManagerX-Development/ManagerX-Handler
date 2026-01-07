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
"""

import asyncio
import yaml
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


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
    
    Examples:
        >>> handler = TranslationHandler()
        >>> text = handler.get("de", "welcome.title", user="Alice")
        >>> text = await handler.get_for_user(bot, 123456, "error.not_found")
    """
    
    TRANSLATION_PATH = Path("translation") / "messages"
    FALLBACK_LANGS = ("en", "de")
    DEFAULT_LANGUAGE = "en"
    
    _cache: TranslationCache = TranslationCache(ttl_minutes=30)
    _file_watchers: Dict[str, float] = {}
    
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
        # Check cache first
        if not force_reload:
            cached = await cls._cache.get(lang_code)
            if cached is not None:
                return cached
        
        # Try loading with fallback chain
        for code in (lang_code, *cls.FALLBACK_LANGS):
            file_path = cls.TRANSLATION_PATH / f"{code}.yaml"
            
            if not file_path.exists():
                continue
            
            try:
                # Check if file was modified
                mtime = file_path.stat().st_mtime
                if code in cls._file_watchers and cls._file_watchers[code] == mtime:
                    cached = await cls._cache.get(code)
                    if cached:
                        return cached
                
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                
                # Validate structure
                if not isinstance(data, dict):
                    logger.warning(f"Invalid YAML structure in {file_path}")
                    continue
                
                # Cache and return
                await cls._cache.set(lang_code, data)
                cls._file_watchers[code] = mtime
                
                if code != lang_code:
                    logger.info(f"Using fallback language '{code}' for '{lang_code}'")
                
                return data
            
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in {file_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error loading {file_path}: {e}")
                continue
        
        # No valid translation found
        logger.warning(f"No translation file found for '{lang_code}' or fallbacks")
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
                logger.debug(f"Invalid path structure at '{key}' in {'.'.join(path)}")
                return default
            value = value.get(key)
            if value is None:
                logger.debug(f"Key not found: {'.'.join(path)}")
                return default
        
        # Ensure final value is string
        if not isinstance(value, str):
            logger.warning(f"Translation at {'.'.join(path)} is not a string")
            return default
        
        # Format placeholders
        try:
            return value.format(**placeholders)
        except KeyError as e:
            logger.warning(f"Missing placeholder in translation: {e}")
            return value
        except Exception as e:
            logger.error(f"Error formatting translation: {e}")
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
            logger.error(f"Error formatting translation: {e}")
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
        lang = cls.DEFAULT_LANGUAGE
        
        # Try to get user's language preference
        try:
            if hasattr(bot, 'settings_db'):
                user_lang = bot.settings_db.get_user_language(user_id)
                if user_lang:
                    lang = user_lang
        except Exception as e:
            logger.debug(f"Could not fetch user language: {e}")
        
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
        lang = cls.DEFAULT_LANGUAGE
        
        try:
            if hasattr(bot, 'settings_db'):
                guild_lang = bot.settings_db.get_guild_language(guild_id)
                if guild_lang:
                    lang = guild_lang
        except Exception as e:
            logger.debug(f"Could not fetch guild language: {e}")
        
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
                logger.debug(f"Error loading translation for {lang}: {e}")
        
        return results
    
    @classmethod
    def get_available_languages(cls) -> List[str]:
        """
        Get list of all available language codes.
        
        Returns:
            List of language codes (e.g., ['en', 'de', 'es'])
        """
        if not cls.TRANSLATION_PATH.exists():
            return [cls.DEFAULT_LANGUAGE]
        
        languages = []
        for file in cls.TRANSLATION_PATH.glob("*.yaml"):
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
            if lang_code != cls.DEFAULT_LANGUAGE:
                default_trans = await cls.load_messages(cls.DEFAULT_LANGUAGE)
                
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
                        f"{len(results['missing_keys'])} keys missing compared to {cls.DEFAULT_LANGUAGE}"
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
        await cls._cache.clear(lang_code)
        if lang_code:
            cls._file_watchers.pop(lang_code, None)
        else:
            cls._file_watchers.clear()
        logger.info(f"Cache cleared: {lang_code or 'all languages'}")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """Get current cache statistics."""
        return cls._cache.get_stats()


# Aliases for backward compatibility
MessagesHandler = TranslationHandler
LangHandler = TranslationHandler
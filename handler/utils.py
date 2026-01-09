"""
Utility Functions
=================

Helper functions for the handler package.
"""

import re
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


async def get_user_language(bot: Any, user_id: int, default: str = "en") -> str:
    """
    Get user's preferred language from bot database.
    
    Args:
        bot: Discord bot instance
        user_id: Discord user ID
        default: Default language if not found
    
    Returns:
        Language code
    """
    try:
        if hasattr(bot, 'settings_db'):
            lang = bot.settings_db.get_user_language(user_id)
            if lang:
                return lang
    except Exception as e:
        logger.debug(f"Could not fetch user language: {e}")
    
    return default


def format_placeholder(text: str, **kwargs) -> str:
    """
    Safely format text with placeholders.
    
    Args:
        text: Text with {placeholders}
        **kwargs: Values to insert
    
    Returns:
        Formatted text (unmatched placeholders remain)
    
    Examples:
        >>> format_placeholder("Hello {name}!", name="Alice")
        'Hello Alice!'
    """
    try:
        return text.format(**kwargs)
    except KeyError:
        # Return original if placeholders missing
        return text
    except Exception as e:
        logger.warning(f"Error formatting text: {e}")
        return text


def validate_language_code(lang_code: str) -> bool:
    """
    Validate language code format.
    
    Args:
        lang_code: Language code to validate
    
    Returns:
        True if valid ISO 639-1 format
    
    Examples:
        >>> validate_language_code("en")
        True
        >>> validate_language_code("eng")
        False
    """
    # ISO 639-1: 2-letter codes
    pattern = r'^[a-z]{2}$'
        
    return bool(re.match(pattern, lang_code.lower()))


class CacheManager:
    """
    Generic cache manager for handler operations.
    
    Provides centralized cache control across all handler modules.
    """
    
    @staticmethod
    async def clear_all() -> Dict[str, bool]:
        """
        Clear all caches in the handler package.
        
        Returns:
            Dictionary with clear status for each cache
        """
        results = {}
        
        try:
            from .translation_handler import TranslationHandler
            await TranslationHandler.clear_cache()
            results["translations"] = True
        except Exception as e:
            logger.error(f"Error clearing translation cache: {e}")
            results["translations"] = False
        
        return results
    
    @staticmethod
    def get_all_stats() -> Dict[str, Any]:
        """
        Get statistics from all caches.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {}
        
        try:
            from .translation_handler import TranslationHandler
            stats["translations"] = TranslationHandler.get_cache_stats()
        except Exception as e:
            logger.error(f"Error getting translation stats: {e}")
            stats["translations"] = {"error": str(e)}
        
        return stats


# Singleton instance
cache_manager = CacheManager()
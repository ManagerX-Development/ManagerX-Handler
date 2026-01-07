"""
ManagerX Handler Library
========================

A comprehensive handler library for Discord bots built with py-cord.
Provides translation management, update checking, and utility functions.

Usage:
    from handler import TranslationHandler, VersionChecker
    from handler import get_user_language, check_for_updates

Author: OPPRO.NET Network
License: MIT
Python: >=3.13
"""

from .translation_handler import TranslationHandler, MessagesHandler, LangHandler
from .update_checker import VersionChecker, UpdateCheckerConfig
from .utils import (
    get_user_language,
    format_placeholder,
    validate_language_code,
    cache_manager
)

__version__ = "1.0.0"
__all__ = [
    # Translation
    "TranslationHandler",
    "MessagesHandler", 
    "LangHandler",
    
    # Update Checker
    "VersionChecker",
    "UpdateCheckerConfig",
    
    # Utils
    "get_user_language",
    "format_placeholder",
    "validate_language_code",
    "cache_manager"
]
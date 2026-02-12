"""
ManagerX Handler Library
========================

A comprehensive handler library for Discord bots built with py-cord.
Provides translation management, update checking, and utility functions.

Usage:
    from managerx_handler import TranslationHandler, VersionChecker
    from managerx_handler import get_user_language, cache_manager

Author: OPPRO.NET Network
License: MIT
Python: >=3.10
"""

# Wir importieren die Klassen direkt aus den Dateien, 
# damit der Nutzer nicht 'managerx_handler.translation_handler.TranslationHandler' schreiben muss.

from .translation_handler import (
    TranslationHandler, 
    TranslationSettings,
    MessagesHandler,
    LangHandler
)

from .update_checker import (
    VersionChecker, 
    UpdateCheckerSettings
)

from .utils import (
    get_user_language,
    format_placeholder,
    validate_language_code,
    cache_manager
)

# Metadaten für PyPI und den Bot
__version__ = "2.0.0"
__author__ = "OPPRO.NET Network"
__license__ = "MIT"

# __all__ steuert, was bei 'from managerx_handler import *' exportiert wird.
# Das sorgt für eine saubere API-Oberfläche.
__all__ = [
    # Translation Core
    "TranslationHandler",
    "TranslationSettings",
    "MessagesHandler",
    "LangHandler",
    
    # Update System
    "VersionChecker",
    "UpdateCheckerConfig",
    
    # Utilities
    "get_user_language",
    "format_placeholder",
    "validate_language_code",
    "cache_manager"
]
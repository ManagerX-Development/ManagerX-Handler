"""
Beispiele für TranslationHandler mit Settings und Logging
===========================================================

Zeigt die Verwendung der neuen Settings-Funktion und des farbigen Loggings.
"""

import asyncio
from translation_handler_extended import TranslationHandler


# ============================================================================
# BEISPIEL 1: Grundlegende Konfiguration
# ============================================================================

def example_basic_config():
    """Einfache Konfiguration mit Standardwerten."""
    print("\n" + "="*60)
    print("BEISPIEL 1: Grundlegende Konfiguration")
    print("="*60 + "\n")
    
    # Konfiguriere einmal beim Start der Anwendung
    TranslationHandler.settings(
        path="translation/messages",  # Pfad zu den YAML-Dateien
        logging=True,                 # Logging aktivieren
        colored=True                  # Farbiges Logging aktivieren
    )
    
    # Ab jetzt sind die Settings für das ganze Projekt aktiv
    print("\nSettings wurden konfiguriert!")
    print(f"Aktuelle Einstellungen: {TranslationHandler.get_settings()}")


# ============================================================================
# BEISPIEL 2: Erweiterte Konfiguration
# ============================================================================

def example_advanced_config():
    """Erweiterte Konfiguration mit allen Optionen."""
    print("\n" + "="*60)
    print("BEISPIEL 2: Erweiterte Konfiguration")
    print("="*60 + "\n")
    
    TranslationHandler.settings(
        path="locales/messages",           # Eigener Pfad
        fallback_langs=("en", "de", "es"), # Mehrere Fallback-Sprachen
        default_lang="de",                 # Deutsch als Standard
        cache_ttl=60,                      # Cache für 60 Minuten
        logging=True,                      # Logging an
        colored=True,                      # Farben an
        log_level="DEBUG"                  # Detailliertes Logging
    )
    
    print("\nErweiterte Settings aktiv!")


# ============================================================================
# BEISPIEL 3: Translations laden und verwenden
# ============================================================================

async def example_load_and_use():
    """Zeigt das Laden von Übersetzungen mit farbigem Logging."""
    print("\n" + "="*60)
    print("BEISPIEL 3: Translations laden")
    print("="*60 + "\n")
    
    # Konfiguriere Settings
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=True,
        log_level="INFO"
    )
    
    # Lade verschiedene Sprachen
    # Die Logs zeigen: [TRANSLATION] de.yaml has loaded (in Grün)
    de_messages = await TranslationHandler.load_messages("de")
    en_messages = await TranslationHandler.load_messages("en")
    
    # Verwende Übersetzungen
    welcome_de = TranslationHandler.get("de", "welcome.title", user="Max")
    welcome_en = TranslationHandler.get("en", "welcome.title", user="Max")
    
    print(f"\nDeutsch: {welcome_de}")
    print(f"English: {welcome_en}")


# ============================================================================
# BEISPIEL 4: Verschiedene Log-Level
# ============================================================================

async def example_log_levels():
    """Zeigt unterschiedliche Log-Level."""
    print("\n" + "="*60)
    print("BEISPIEL 4: Log-Level Demonstration")
    print("="*60 + "\n")
    
    # DEBUG Level - Zeigt alles
    print("\n--- DEBUG Level ---")
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=True,
        log_level="DEBUG"
    )
    await TranslationHandler.load_messages("de")
    
    # INFO Level - Zeigt nur wichtige Infos
    print("\n--- INFO Level ---")
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=True,
        log_level="INFO"
    )
    await TranslationHandler.clear_cache()
    await TranslationHandler.load_messages("en")
    
    # WARNING Level - Zeigt nur Warnungen und Fehler
    print("\n--- WARNING Level ---")
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=True,
        log_level="WARNING"
    )
    await TranslationHandler.clear_cache()
    await TranslationHandler.load_messages("es")  # Könnte Warnung erzeugen


# ============================================================================
# BEISPIEL 5: Ohne Colorama (Fallback)
# ============================================================================

def example_no_color():
    """Zeigt Logging ohne Colorama."""
    print("\n" + "="*60)
    print("BEISPIEL 5: Logging ohne Farben")
    print("="*60 + "\n")
    
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=False  # Farben deaktiviert
    )
    
    print("\nLogging ohne Farben ist aktiviert!")


# ============================================================================
# BEISPIEL 6: Praktische Verwendung in Discord Bot
# ============================================================================

async def example_discord_bot_usage():
    """Beispiel für die Verwendung in einem Discord Bot."""
    print("\n" + "="*60)
    print("BEISPIEL 6: Discord Bot Integration")
    print("="*60 + "\n")
    
    # In der main() Funktion deines Bots, EINMAL beim Start:
    TranslationHandler.settings(
        path="bot/locales/messages",
        fallback_langs=("en", "de"),
        default_lang="en",
        cache_ttl=45,
        logging=True,
        colored=True,
        log_level="INFO"
    )
    
    # Danach kannst du überall in deinem Bot Translations verwenden:
    
    # In einem Command:
    error_msg = TranslationHandler.get(
        "de", 
        "error.command_failed", 
        command="ping"
    )
    print(f"Fehlermeldung: {error_msg}")
    
    # Für einen spezifischen User (async):
    class MockBot:
        pass
    
    bot = MockBot()
    user_msg = await TranslationHandler.get_for_user(
        bot,
        123456789,
        "welcome.message",
        username="TestUser"
    )
    print(f"User Nachricht: {user_msg}")


# ============================================================================
# BEISPIEL 7: Cache Management
# ============================================================================

async def example_cache_management():
    """Zeigt Cache-Verwaltung mit Logging."""
    print("\n" + "="*60)
    print("BEISPIEL 7: Cache Management")
    print("="*60 + "\n")
    
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,
        colored=True,
        cache_ttl=30
    )
    
    # Lade Sprachen
    await TranslationHandler.load_messages("de")
    await TranslationHandler.load_messages("en")
    
    # Zeige Cache Stats
    stats = TranslationHandler.get_cache_stats()
    print(f"\nCache Stats: {stats}")
    
    # Lösche Cache für eine Sprache
    await TranslationHandler.clear_cache("de")
    print("\nCache für DE gelöscht")
    
    # Lösche gesamten Cache
    await TranslationHandler.clear_cache()
    print("Gesamter Cache gelöscht\n")


# ============================================================================
# BEISPIEL 8: Logging deaktivieren für Production
# ============================================================================

def example_production_mode():
    """Konfiguration für Production ohne detailliertes Logging."""
    print("\n" + "="*60)
    print("BEISPIEL 8: Production Mode")
    print("="*60 + "\n")
    
    TranslationHandler.settings(
        path="translation/messages",
        logging=True,           # Basis-Logging an
        colored=False,          # Keine Farben in Logs
        log_level="ERROR"       # Nur Fehler loggen
    )
    
    print("Production Settings aktiv - nur Fehler werden geloggt")


# ============================================================================
# BEISPIEL 9: Settings anzeigen
# ============================================================================

def example_show_settings():
    """Zeigt alle aktuellen Settings."""
    print("\n" + "="*60)
    print("BEISPIEL 9: Aktuelle Settings anzeigen")
    print("="*60 + "\n")
    
    # Konfiguriere
    TranslationHandler.settings(
        path="my/custom/path",
        default_lang="de",
        logging=True,
        colored=True
    )
    
    # Hole alle Settings
    settings = TranslationHandler.get_settings()
    
    print("Aktuelle Konfiguration:")
    print("-" * 40)
    for key, value in settings.items():
        print(f"{key:.<25} {value}")


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

async def main():
    """Führt alle Beispiele aus."""
    print("\n" + "="*70)
    print("TranslationHandler - Settings & Logging Beispiele")
    print("="*70)
    
    # Beispiele ausführen
    example_basic_config()
    example_advanced_config()
    
    await example_load_and_use()
    await example_log_levels()
    
    example_no_color()
    
    await example_discord_bot_usage()
    await example_cache_management()
    
    example_production_mode()
    example_show_settings()
    
    print("\n" + "="*70)
    print("Alle Beispiele abgeschlossen!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Führe alle Beispiele aus
    asyncio.run(main())
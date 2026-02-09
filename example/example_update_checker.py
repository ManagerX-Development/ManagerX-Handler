"""
Beispiele für VersionChecker mit Settings und Logging
======================================================

Zeigt die Verwendung der neuen Settings-Funktion und des farbigen Loggings.
"""

import asyncio
from update_checker_extended import VersionChecker, VersionInfo


# ============================================================================
# BEISPIEL 1: Grundlegende Konfiguration
# ============================================================================

def example_basic_config():
    """Einfache Konfiguration mit Standardwerten."""
    print("\n" + "="*60)
    print("BEISPIEL 1: Grundlegende Konfiguration")
    print("="*60 + "\n")
    
    # Konfiguriere einmal beim Start der Anwendung
    VersionChecker.settings(
        github_repo="https://github.com/Oppro-net-Development/ManagerX",
        version_file="config/version.txt",  # Liest Version automatisch
        logging=True,                       # Logging aktivieren
        colored=True                        # Farbiges Logging aktivieren
    )
    
    print("\nSettings wurden konfiguriert!")
    print(f"Aktuelle Einstellungen: {VersionChecker.get_settings()}")


# ============================================================================
# BEISPIEL 2: Erweiterte Konfiguration
# ============================================================================

def example_advanced_config():
    """Erweiterte Konfiguration mit allen Optionen."""
    print("\n" + "="*60)
    print("BEISPIEL 2: Erweiterte Konfiguration")
    print("="*60 + "\n")
    
    VersionChecker.settings(
        github_repo="https://github.com/user/my-bot",
        version_url="https://raw.githubusercontent.com/user/my-bot/main/version.txt",
        version_file="config/version.txt",  # Lokale Version-Datei
        timeout=15,                         # 15 Sekunden Timeout
        check_interval=12,                  # Alle 12 Stunden prüfen
        logging=True,                       # Logging an
        colored=True,                       # Farben an
        log_level="DEBUG",                  # Detailliertes Logging
        auto_check=True,                    # Auto-Check beim Start
        show_console=True                   # Konsolen-Ausgaben zeigen
    )
    
    print("\nErweiterte Settings aktiv!")


# ============================================================================
# BEISPIEL 3: Version Checker initialisieren und verwenden
# ============================================================================

async def example_version_check():
    """Zeigt die grundlegende Verwendung des Version Checkers."""
    print("\n" + "="*60)
    print("BEISPIEL 3: Version Check")
    print("="*60 + "\n")
    
    # Konfiguriere Settings
    VersionChecker.settings(
        github_repo="https://github.com/Oppro-net-Development/ManagerX",
        logging=True,
        colored=True,
        log_level="INFO"
    )
    
    # Erstelle Checker (mit manueller Version)
    checker = VersionChecker("1.7.2-alpha")
    
    # Prüfe auf Updates
    # Die Logs zeigen: [UPDATE] Checking for updates...
    #                  [UPDATE] Latest version fetched: 1.7.2
    update_info = await checker.check_for_updates()
    
    print("\nUpdate Information:")
    print(f"  Update verfügbar: {update_info['update_available']}")
    print(f"  Aktuelle Version: {update_info['current_version']}")
    print(f"  Neueste Version:  {update_info['latest_version']}")
    print(f"  Dev Build:        {update_info['is_dev_build']}")
    print(f"  Pre-Release:      {update_info['is_prerelease']}")


# ============================================================================
# BEISPIEL 4: Auto-Read Version aus Datei
# ============================================================================

async def example_auto_read_version():
    """Zeigt automatisches Lesen der Version aus Datei."""
    print("\n" + "="*60)
    print("BEISPIEL 4: Auto-Read Version")
    print("="*60 + "\n")
    
    # Erstelle Beispiel version.txt
    from pathlib import Path
    Path("config").mkdir(exist_ok=True)
    Path("config/version.txt").write_text("1.7.2-alpha")
    
    # Konfiguriere mit version_file
    VersionChecker.settings(
        version_file="config/version.txt",
        logging=True,
        colored=True
    )
    
    # Erstelle Checker OHNE Version-Parameter
    # Version wird automatisch aus Datei gelesen!
    checker = VersionChecker()
    
    print(f"\nAutomatisch gelesene Version: {checker.current_version}")
    
    # Zeige Version-Info
    info = checker.get_version_info()
    print(f"Major: {info['major']}")
    print(f"Minor: {info['minor']}")
    print(f"Patch: {info['patch']}")
    print(f"Release Type: {info['release_type']}")


# ============================================================================
# BEISPIEL 5: Console Output mit verschiedenen Status
# ============================================================================

async def example_console_output():
    """Zeigt verschiedene Console-Ausgaben."""
    print("\n" + "="*60)
    print("BEISPIEL 5: Console Output Beispiele")
    print("="*60 + "\n")
    
    VersionChecker.settings(
        github_repo="https://github.com/Oppro-net-Development/ManagerX",
        logging=True,
        colored=True,
        show_console=True
    )
    
    # Fall 1: Update verfügbar
    print("\n--- Update verfügbar ---")
    checker1 = VersionChecker("1.0.0")
    await checker1.print_update_status()
    
    # Fall 2: Up-to-date
    print("\n--- Aktuell ---")
    checker2 = VersionChecker("1.7.2")
    await checker2.print_update_status()
    
    # Fall 3: Dev Build
    print("\n--- Dev Build ---")
    checker3 = VersionChecker("2.0.0-dev")
    await checker3.print_update_status()


# ============================================================================
# BEISPIEL 6: Verschiedene Log-Level
# ============================================================================

async def example_log_levels():
    """Zeigt unterschiedliche Log-Level."""
    print("\n" + "="*60)
    print("BEISPIEL 6: Log-Level Demonstration")
    print("="*60 + "\n")
    
    # DEBUG Level - Zeigt alles
    print("\n--- DEBUG Level ---")
    VersionChecker.settings(
        logging=True,
        colored=True,
        log_level="DEBUG"
    )
    checker = VersionChecker("1.7.2")
    await checker.check_for_updates()
    
    # INFO Level - Zeigt nur wichtige Infos
    print("\n--- INFO Level ---")
    VersionChecker.settings(
        logging=True,
        colored=True,
        log_level="INFO"
    )
    checker = VersionChecker("1.7.2")
    await checker.check_for_updates(force=True)
    
    # WARNING Level - Zeigt nur Warnungen und Fehler
    print("\n--- WARNING Level ---")
    VersionChecker.settings(
        logging=True,
        colored=True,
        log_level="WARNING"
    )
    checker = VersionChecker("1.7.2")
    await checker.check_for_updates(force=True)


# ============================================================================
# BEISPIEL 7: Discord Bot Integration
# ============================================================================

async def example_discord_bot():
    """Beispiel für die Verwendung in einem Discord Bot."""
    print("\n" + "="*60)
    print("BEISPIEL 7: Discord Bot Integration")
    print("="*60 + "\n")
    
    # In der main() Funktion deines Bots, EINMAL beim Start:
    VersionChecker.settings(
        github_repo="https://github.com/user/my-discord-bot",
        version_file="config/version.txt",
        logging=True,
        colored=True,
        log_level="INFO",
        auto_check=True,      # Prüft automatisch beim Start
        show_console=True
    )
    
    # Erstelle Checker (liest Version automatisch)
    checker = VersionChecker()
    
    # Bei Bot-Start: Zeige Update-Status
    await checker.print_update_status()
    
    # In einem Admin-Command: Manuell auf Updates prüfen
    update_info = await checker.check_for_updates(force=True)
    
    if update_info["update_available"]:
        print(f"\n✨ Neue Version verfügbar: {update_info['latest_version']}")
        print(f"Download: {update_info['download_url']}")


# ============================================================================
# BEISPIEL 8: Version Parsing und Vergleich
# ============================================================================

def example_version_parsing():
    """Zeigt Version Parsing und Vergleiche."""
    print("\n" + "="*60)
    print("BEISPIEL 8: Version Parsing")
    print("="*60 + "\n")
    
    # Parse verschiedene Version-Formate
    v1 = VersionChecker.parse_version("1.7.2")
    v2 = VersionChecker.parse_version("1.7.2-alpha")
    v3 = VersionChecker.parse_version("2.0.0-beta")
    v4 = VersionChecker.parse_version("2.1.0")
    
    print("Geparste Versionen:")
    print(f"  v1: {v1} (stable: {v1.is_stable()})")
    print(f"  v2: {v2} (prerelease: {v2.is_prerelease()})")
    print(f"  v3: {v3} (prerelease: {v3.is_prerelease()})")
    print(f"  v4: {v4} (stable: {v4.is_stable()})")
    
    # Vergleiche
    print("\nVergleiche:")
    print(f"  v1 < v4: {v1 < v4}")
    print(f"  v2 == v1: {v2 == v1}")  # Gleiche Core-Version
    print(f"  v3 < v4: {v3 < v4}")
    
    # Core-Versionen
    print("\nCore-Versionen (ohne Release-Type):")
    print(f"  v1.core: {v1.core}")
    print(f"  v2.core: {v2.core}")
    print(f"  v3.core: {v3.core}")


# ============================================================================
# BEISPIEL 9: Production vs Development Setup
# ============================================================================

def example_prod_vs_dev():
    """Zeigt Production vs Development Konfiguration."""
    print("\n" + "="*60)
    print("BEISPIEL 9: Production vs Development")
    print("="*60 + "\n")
    
    import os
    
    # Development Setup
    if os.getenv("DEBUG") == "true":
        print("\n--- Development Mode ---")
        VersionChecker.settings(
            logging=True,
            colored=True,
            log_level="DEBUG",        # Detailliert
            show_console=True,        # Alles zeigen
            auto_check=True           # Auto-Check aktiv
        )
    else:
        # Production Setup
        print("\n--- Production Mode ---")
        VersionChecker.settings(
            logging=True,
            colored=False,            # Keine Farben in Logs
            log_level="WARNING",      # Nur Warnungen
            show_console=False,       # Keine Console-Ausgaben
            auto_check=False          # Manuell checken
        )
    
    print("Konfiguration abgeschlossen!")


# ============================================================================
# BEISPIEL 10: Cached Results
# ============================================================================

async def example_caching():
    """Zeigt Caching-Funktionalität."""
    print("\n" + "="*60)
    print("BEISPIEL 10: Caching")
    print("="*60 + "\n")
    
    VersionChecker.settings(
        check_interval=24,  # Cache für 24 Stunden
        logging=True,
        colored=True,
        log_level="DEBUG"
    )
    
    checker = VersionChecker("1.7.2")
    
    # Erster Check - Fetched von Remote
    print("\n--- Erster Check ---")
    await checker.check_for_updates()
    
    # Zweiter Check - Verwendet Cache
    print("\n--- Zweiter Check (cached) ---")
    await checker.check_for_updates()
    
    # Dritter Check - Force, ignoriert Cache
    print("\n--- Dritter Check (force) ---")
    await checker.check_for_updates(force=True)


# ============================================================================
# BEISPIEL 11: Settings anzeigen
# ============================================================================

def example_show_settings():
    """Zeigt alle aktuellen Settings."""
    print("\n" + "="*60)
    print("BEISPIEL 11: Aktuelle Settings anzeigen")
    print("="*60 + "\n")
    
    # Konfiguriere
    VersionChecker.settings(
        github_repo="https://github.com/user/bot",
        version_file="config/version.txt",
        timeout=20,
        check_interval=12,
        logging=True,
        colored=True,
        log_level="INFO"
    )
    
    # Hole alle Settings
    settings = VersionChecker.get_settings()
    
    print("Aktuelle Konfiguration:")
    print("-" * 50)
    for key, value in settings.items():
        print(f"{key:.<30} {value}")


# ============================================================================
# BEISPIEL 12: Fehlerbehandlung
# ============================================================================

async def example_error_handling():
    """Zeigt Fehlerbehandlung."""
    print("\n" + "="*60)
    print("BEISPIEL 12: Fehlerbehandlung")
    print("="*60 + "\n")
    
    # Ungültige Version
    print("\n--- Ungültige Version ---")
    invalid_version = VersionChecker.parse_version("invalid.version.string")
    print(f"Parsed: {invalid_version}")
    print(f"Type: {invalid_version.release_type.value}")
    
    # Netzwerk-Fehler simulieren (falscher URL)
    print("\n--- Netzwerk-Fehler ---")
    VersionChecker.settings(
        version_url="https://invalid.url.example.com/version.txt",
        timeout=5,
        logging=True,
        colored=True
    )
    
    checker = VersionChecker("1.0.0")
    result = await checker.check_for_updates()
    
    if "error" in result:
        print(f"Fehler erkannt: {result['error']}")


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================

async def main():
    """Führt alle Beispiele aus."""
    print("\n" + "="*70)
    print("VersionChecker - Settings & Logging Beispiele")
    print("="*70)
    
    # Beispiele ausführen
    example_basic_config()
    example_advanced_config()
    
    await example_version_check()
    await example_auto_read_version()
    await example_console_output()
    await example_log_levels()
    
    await example_discord_bot()
    
    example_version_parsing()
    example_prod_vs_dev()
    
    await example_caching()
    
    example_show_settings()
    await example_error_handling()
    
    print("\n" + "="*70)
    print("Alle Beispiele abgeschlossen!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Führe alle Beispiele aus
    asyncio.run(main())
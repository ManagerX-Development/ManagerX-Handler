# ManagerX Handler Library

🚀 **Comprehensive handler library for Discord bots built with py-cord**

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/managerx-handler)](https://pypi.org/project/managerx-handler/)
[![License](https://img.shields.io/badge/license-GPL.3-0-green.svg)](LICENSE)
[![ManagerX](https://img.shields.io/badge/ManagerX-Ecosystem-blueviolet)](https://github.com/Oppro-net-Development/ManagerX)

> **Part of the ManagerX Ecosystem** - A modular Discord bot framework by OPPRO.NET Network

This library is an official component of the [ManagerX Discord Bot](https://github.com/ManagerX-Development/ManagerX) project, designed to be used as a standalone package or integrated into the main bot. It provides core functionality for translation management, version checking, and common utilities that power ManagerX and can be used in any py-cord based bot.

## Features

✨ **Translation Management**
- YAML-based multi-language support
- Automatic fallback system
- User & guild-specific languages
- Hot-reload capability
- Advanced caching with TTL

🔄 **Update Checker**
- Semantic versioning support
- GitHub integration
- Pre-release detection
- Automatic notifications
- Release notes fetching

⚡ **Performance**
- Fully async/await
- Intelligent caching
- Non-blocking operations
- Memory efficient

🛡️ **Type Safety**
- Full type hints
- MyPy compatible
- IDE autocomplete support

## Installation

```bash
pip install managerx-handler
```

Or with development dependencies:

```bash
pip install managerx-handler[dev]
```

## Quick Start

### Translation Handler

```python
from handler import TranslationHandler

# Setup translation directory structure:
# translation/
#   messages/
#     en.yaml
#     de.yaml
#     es.yaml

# Synchronous usage
text = TranslationHandler.get("en", "welcome.title", user="Alice")
# Output: "Welcome, Alice!"

# Async usage
text = await TranslationHandler.get_async("de", "error.not_found")

# User-specific translation
text = await TranslationHandler.get_for_user(
    bot, 
    user_id=123456, 
    path="settings.updated"
)

# Guild-specific translation
text = await TranslationHandler.get_for_guild(
    bot,
    guild_id=789012,
    path="welcome.message"
)

# Get all available languages
languages = TranslationHandler.get_available_languages()
# Output: ['en', 'de', 'es']

# Get translations in all languages
all_trans = await TranslationHandler.get_all_translations("language.name")
# Output: {'en': 'English', 'de': 'Deutsch', 'es': 'Español'}

# Validate translation files
validation = await TranslationHandler.validate_translations("de")
print(validation["missing_keys"])  # Keys missing compared to default language

# Clear cache
await TranslationHandler.clear_cache()  # Clear all
await TranslationHandler.clear_cache("de")  # Clear specific language

# Get cache statistics
stats = TranslationHandler.get_cache_stats()
print(f"Cached languages: {stats['entries']}")
```

### Update Checker

```python
from handler import VersionChecker

# Initialize checker
checker = VersionChecker("1.7.2-alpha")

# Check for updates
update_info = await checker.check_for_updates()

if update_info["update_available"]:
    print(f"New version: {update_info['latest_version']}")
    print(f"Release notes: {update_info['release_notes']}")
    print(f"Download: {update_info['download_url']}")

# Print formatted status to console
await checker.print_update_status()

# Get detailed version info
info = checker.get_version_info()
print(f"Major: {info['major']}, Minor: {info['minor']}, Patch: {info['patch']}")
print(f"Release type: {info['release_type']}")
print(f"Is stable: {info['is_stable']}")

# Parse version string
version = VersionChecker.parse_version("2.0.0-beta")
print(f"{version.major}.{version.minor}.{version.patch}")  # 2.0.0
print(version.is_prerelease())  # True
```

### Utility Functions

```python
from handler import get_user_language, format_placeholder, validate_language_code

# Get user language
lang = await get_user_language(bot, user_id=123456, default="en")

# Safe placeholder formatting
text = format_placeholder(
    "Hello {name}, you have {count} messages!",
    name="Alice",
    count=5
)

# Validate language code
is_valid = validate_language_code("en")  # True
is_valid = validate_language_code("eng")  # False
```

### Cache Management

```python
from handler import cache_manager

# Clear all caches
results = await cache_manager.clear_all()
print(results)  # {'translations': True}

# Get cache statistics
stats = cache_manager.get_all_stats()
print(stats['translations'])
```

## Translation File Format

Create YAML files in `translation/messages/`:

**en.yaml:**
```yaml
welcome:
  title: "Welcome, {user}!"
  description: "Welcome to {server}"
  
error:
  not_found: "Item not found"
  invalid_input: "Invalid input: {field}"
  
settings:
  updated: "Settings updated successfully"
  language_changed: "Language changed to English"
  
language:
  name: "English"
```

**de.yaml:**
```yaml
welcome:
  title: "Willkommen, {user}!"
  description: "Willkommen auf {server}"
  
error:
  not_found: "Element nicht gefunden"
  invalid_input: "Ungültige Eingabe: {field}"
  
settings:
  updated: "Einstellungen erfolgreich aktualisiert"
  language_changed: "Sprache auf Deutsch geändert"
  
language:
  name: "Deutsch"
```

## Advanced Features

### Custom Configuration

```python
from handler import UpdateCheckerConfig, VersionChecker

# Custom configuration
config = UpdateCheckerConfig()
config.GITHUB_REPO = "https://github.com/your-org/your-bot"
config.VERSION_URL = "https://raw.githubusercontent.com/your-org/your-bot/main/version.txt"
config.TIMEOUT = 15
config.CHECK_INTERVAL = 12  # hours

checker = VersionChecker("1.0.0", config=config)
```

### Translation Cache Control

```python
from handler import TranslationHandler

# Custom cache TTL
TranslationHandler._cache = TranslationCache(ttl_minutes=60)

# Force reload from disk
messages = await TranslationHandler.load_messages("en", force_reload=True)

# Monitor file changes
stats = TranslationHandler.get_cache_stats()
print(f"Oldest cache entry: {stats['oldest_entry']}")
```

### Version Comparison

```python
from handler import VersionChecker

v1 = VersionChecker.parse_version("1.5.0")
v2 = VersionChecker.parse_version("2.0.0")

if v2 > v1:
    print("v2 is newer")

# Compare only core version (ignore pre-release type)
print(v1.core)  # (1, 5, 0)
print(v2.core)  # (2, 0, 0)
```

## Integration with Py-Cord

```python
import discord
from discord.ext import commands
from handler import TranslationHandler, VersionChecker

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")
    
    # Check for updates on startup
    checker = VersionChecker("1.7.2")
    await checker.print_update_status()

@bot.slash_command(name="language", description="Change your language")
async def set_language(
    ctx: discord.ApplicationContext,
    language: discord.Option(str, choices=["en", "de", "es"])
):
    # Save to database
    bot.settings_db.set_user_language(ctx.author.id, language)
    
    # Get translated confirmation
    message = await TranslationHandler.get_for_user(
        bot,
        ctx.author.id,
        "settings.language_changed"
    )
    
    await ctx.respond(message)

@bot.slash_command(name="welcome")
async def welcome_command(ctx: discord.ApplicationContext):
    # Automatic user language detection
    message = await TranslationHandler.get_for_user(
        bot,
        ctx.author.id,
        "welcome.title",
        user=ctx.author.name,
        server=ctx.guild.name
    )
    
    await ctx.respond(message)

bot.run("YOUR_TOKEN")
```

## Error Handling

```python
from handler import TranslationHandler
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# All methods handle errors gracefully
text = TranslationHandler.get(
    "invalid_lang",
    "invalid.path",
    default="Fallback text"
)
# Returns "Fallback text" instead of raising exception

# Validation for debugging
validation = await TranslationHandler.validate_translations("de")
if not validation["valid"]:
    print("Errors:", validation["errors"])
    print("Missing keys:", validation["missing_keys"])
```

## Testing

```bash
# Install dev dependencies
pip install managerx-handler[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=handler

# Type checking
mypy handler/

# Format code
black handler/

# Lint
ruff check handler/
```

## Project Structure

```
managerx-handler/
├── handler/
│   ├── __init__.py
│   ├── translation_handler.py
│   ├── update_checker.py
│   ├── utils.py
│   └── py.typed
├── tests/
│   ├── test_translation.py
│   └── test_version.py
├── translation/
│   └── messages/
│       ├── en.yaml
│       └── de.yaml
├── pyproject.toml
├── README.md
└── LICENSE
```

## Requirements

- Python >= 3.13
- aiohttp >= 3.9.0
- PyYAML >= 6.0
- py-cord >= 2.6.0
- colorama >= 0.4.6

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://docs.oppro.net/managerx-handler)
- 🐛 [Issue Tracker](https://github.com/Oppro-net-Development/managerx-handler/issues)
- 💬 [Discord Support](https://discord.gg/oppro)

## Credits

Developed by [OPPRO.NET Network](https://oppro.net) for the ManagerX Discord bot project.

### ManagerX Ecosystem

This library is part of the **ManagerX Ecosystem**, a collection of tools and libraries for building powerful Discord bots:

- **[ManagerX](https://github.com/Oppro-net-Development/ManagerX)** - The main Discord bot (Ultimate server management and automation)
- **[managerx-handler](https://github.com/Oppro-net-Development/managerx-handler)** - Handler library (this package)
- **ManagerX DevTools** - Development and debugging tools (coming soon)
- **ManagerX API** - RESTful API interface (coming soon)

All components are designed to work together seamlessly while remaining independently usable.

---

Made with ❤️ for the Discord bot community

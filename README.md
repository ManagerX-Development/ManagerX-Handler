# TranslationHandler - Extended Edition

Extended Translation Handler with configurable settings and colored logging for Discord bots.

## 🎨 New Features

### ✨ Settings Function
- **One-Time Configuration**: Set settings once, use everywhere
- **Flexible Path**: Configure your own translations folder
- **Customizable Fallbacks**: Configure multiple fallback languages
- **Cache Control**: Individually set TTL (Time-to-Live)

### 🌈 Colored Logging
- **Colorama Integration**: Color-coded log outputs
- **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Automatic Fallback**: Works without Colorama too
- **Clear Outputs**: Easily recognizable translation logs

## 📦 Installation

```bash
# Basic module
pip install pyyaml

# Optional: For colored logging
pip install colorama
```

## 🚀 Quick Start

### 1. One-Time Configuration at Startup

```python
from translation_handler_extended import TranslationHandler

# In your main() function - once at bot startup
TranslationHandler.settings(
    path="translation/messages",  # Path to your YAML files
    logging=True,                 # Enable logging
    colored=True                  # Enable colored logging
)
```

### 2. Use Throughout Your Project

```python
# Synchronous
text = TranslationHandler.get("de", "welcome.title", user="Max")

# Asynchronous
text = await TranslationHandler.get_async("en", "error.not_found")

# For specific user
text = await TranslationHandler.get_for_user(bot, user_id, "message.greeting")
```

## 📖 Settings Options

### All Available Parameters

```python
TranslationHandler.settings(
    path="translation/messages",         # Path to YAML files
    fallback_langs=("en", "de"),        # Fallback languages (Tuple)
    default_lang="en",                   # Default language
    cache_ttl=30,                        # Cache TTL in minutes
    logging=True,                        # Enable/disable logging
    colored=True,                        # Colored logging
    log_level="INFO"                     # DEBUG, INFO, WARNING, ERROR
)
```

### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | str/Path | `"translation/messages"` | Folder with YAML files |
| `fallback_langs` | tuple | `("en", "de")` | Fallback languages in order |
| `default_lang` | str | `"en"` | Default language |
| `cache_ttl` | int | `30` | Cache validity in minutes |
| `logging` | bool | `True` | Enable translation logs |
| `colored` | bool | `True` | Colored console output |
| `log_level` | str | `"INFO"` | Logging level |

## 🎨 Log Outputs

### Log Colors (with Colorama)

```
[TRANSLATION] de.yaml has loaded              # Green (Success)
[TRANSLATION] en.yaml loaded (fallback...)    # Green (Info)
[TRANSLATION] Loaded de.yaml from cache       # Cyan (Debug)
[TRANSLATION] File not found: es.yaml         # Yellow (Warning)
[TRANSLATION] YAML parsing error...           # Red (Error)
```

### Log Level Examples

```python
# DEBUG - Shows everything (including cache accesses)
TranslationHandler.settings(log_level="DEBUG")
# Output:
# [TRANSLATION] Loaded de.yaml from cache
# [TRANSLATION] Key not found: some.missing.key

# INFO - Standard (important events)
TranslationHandler.settings(log_level="INFO")
# Output:
# [TRANSLATION] de.yaml has loaded
# [TRANSLATION] Cache cleared for: de

# WARNING - Only warnings and errors
TranslationHandler.settings(log_level="WARNING")
# Output:
# [TRANSLATION] No translation file found for 'xx'

# ERROR - Only critical errors
TranslationHandler.settings(log_level="ERROR")
# Output:
# [TRANSLATION] YAML parsing error in de.yaml: ...
```

## 💡 Usage Examples

### Discord Bot Integration

```python
import discord
from discord.ext import commands
from translation_handler_extended import TranslationHandler

# Bot Setup
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    # Configure settings ONCE at startup
    TranslationHandler.settings(
        path="bot/translations/messages",
        fallback_langs=("en", "de", "es"),
        default_lang="en",
        cache_ttl=60,
        logging=True,
        colored=True,
        log_level="INFO"
    )
    
    print(f"{bot.user} is ready!")
    # Output: [TRANSLATION] en.yaml has loaded

@bot.command()
async def hello(ctx):
    # Automatic user language
    greeting = await TranslationHandler.get_for_user(
        bot,
        ctx.author.id,
        "commands.hello.message",
        username=ctx.author.name
    )
    await ctx.send(greeting)

@bot.command()
async def error_demo(ctx):
    # Manual language with placeholders
    error_msg = TranslationHandler.get(
        "de",
        "errors.command_failed",
        command="demo",
        reason="Test"
    )
    await ctx.send(error_msg)

bot.run("TOKEN")
```

### Development vs Production

```python
# Development - Detailed logging
if DEBUG:
    TranslationHandler.settings(
        path="translations/messages",
        logging=True,
        colored=True,
        log_level="DEBUG"
    )
else:
    # Production - Minimal logging
    TranslationHandler.settings(
        path="translations/messages",
        logging=True,
        colored=False,  # No colors in logs
        log_level="ERROR"  # Only errors
    )
```

### Custom Path Structure

```python
# Project structure:
# my_bot/
# ├── locales/
# │   └── lang/
# │       ├── en.yaml
# │       ├── de.yaml
# │       └── fr.yaml
# └── bot.py

TranslationHandler.settings(
    path="locales/lang",  # Custom path
    fallback_langs=("en", "de", "fr"),
    default_lang="en"
)
```

### Cache Management

```python
# Show cache stats
stats = TranslationHandler.get_cache_stats()
print(stats)
# Output: {'entries': 2, 'languages': ['de', 'en'], 'oldest_entry': ...}

# Clear cache for one language
await TranslationHandler.clear_cache("de")
# Output: [TRANSLATION] Cache cleared for: de

# Clear entire cache
await TranslationHandler.clear_cache()
# Output: [TRANSLATION] Cache cleared for all languages

# Show settings
settings = TranslationHandler.get_settings()
print(settings)
```

## 🔧 Advanced Features

### Multiple Fallback Languages

```python
TranslationHandler.settings(
    fallback_langs=("en", "de", "es", "fr")
)

# If "it.yaml" is missing:
# 1. Tries it.yaml
# 2. Tries en.yaml (Fallback 1)
# 3. Tries de.yaml (Fallback 2)
# 4. Tries es.yaml (Fallback 3)
# 5. Tries fr.yaml (Fallback 4)
text = await TranslationHandler.load_messages("it")
```

### Hot-Reload Support

```python
# Force reload from disk (ignores cache)
messages = await TranslationHandler.load_messages("de", force_reload=True)
# Output: [TRANSLATION] de.yaml has loaded
```

### Get Settings

```python
# All current settings
current_settings = TranslationHandler.get_settings()

print(current_settings)
# {
#     'translation_path': 'translation/messages',
#     'fallback_languages': ('en', 'de'),
#     'default_language': 'en',
#     'cache_ttl_minutes': 30,
#     'logging_enabled': True,
#     'colored_logging': True,
#     'log_level': 'INFO',
#     'configured': True,
#     'colorama_available': True
# }
```

## 📝 YAML File Structure

```yaml
# en.yaml
welcome:
  title: "Welcome, {user}!"
  message: "Hello and welcome to our server!"

commands:
  hello:
    message: "Hi {username}, how are you?"
  
errors:
  command_failed: "Command '{command}' failed: {reason}"
  not_found: "Item not found"
  cooldown: "Please wait {seconds} seconds"

settings:
  language_name: "English"
```

## 🎯 Best Practices

### 1. Configure Settings at Startup

```python
# ✅ CORRECT - Once at bot startup
async def main():
    TranslationHandler.settings(
        path="translations/messages",
        logging=True,
        colored=True
    )
    
    bot = commands.Bot(...)
    await bot.start(TOKEN)

# ❌ WRONG - Not in every command
@bot.command()
async def test(ctx):
    TranslationHandler.settings(...)  # DON'T DO THIS!
```

### 2. Use Async Methods in Async Context

```python
# ✅ CORRECT - In async functions
async def my_function():
    text = await TranslationHandler.get_async("de", "key")

# ✅ ALSO OK - Sync wrapper for sync context
def sync_function():
    text = TranslationHandler.get("de", "key")  # Uses asyncio internally
```

### 3. Adjust Log Level by Environment

```python
import os

log_level = "DEBUG" if os.getenv("DEBUG") else "ERROR"

TranslationHandler.settings(
    logging=True,
    log_level=log_level
)
```

### 4. Validate Placeholders

```python
# ✅ CORRECT - Provide all placeholders
text = TranslationHandler.get(
    "de", 
    "error.timeout",
    seconds=30,
    action="connect"
)

# ⚠️ WARNING - Missing placeholders
text = TranslationHandler.get("de", "error.timeout")
# Output: [TRANSLATION] Missing placeholder in translation: 'seconds'
```

## 🐛 Troubleshooting

### Colorama Not Available

```python
# Automatic fallback to uncolored logging
# No action needed - works automatically

# Or explicitly disable:
TranslationHandler.settings(colored=False)
```

### YAML Files Not Found

```python
# Check the path
settings = TranslationHandler.get_settings()
print(f"Searching in: {settings['translation_path']}")

# Check available languages
langs = TranslationHandler.get_available_languages()
print(f"Found: {langs}")
```

### Cache Issues

```python
# Clear cache completely and reload
await TranslationHandler.clear_cache()
messages = await TranslationHandler.load_messages("de", force_reload=True)
```

## 📊 Performance

- **Cache**: TTL-based, automatic cleanup
- **File Watching**: Only reload on changes (via mtime)
- **Async Support**: Fully asynchronous for best performance
- **Memory**: Efficient memory usage through TTL

## 🔄 Migration from Old Version

```python
# OLD
TRANSLATION_PATH = Path("translation") / "messages"
messages = MessagesHandler.load_messages("de")

# NEW
TranslationHandler.settings(path="translation/messages")
messages = await TranslationHandler.load_messages("de")
# Output: [TRANSLATION] de.yaml has loaded
```

## 📚 API Reference

### Settings Methods

```python
TranslationHandler.settings(...)      # Set configuration
TranslationHandler.get_settings()     # Get current config
```

### Translation Methods

```python
TranslationHandler.get(lang, path, **kwargs)                    # Sync
await TranslationHandler.get_async(lang, path, **kwargs)        # Async
await TranslationHandler.get_for_user(bot, user_id, path)       # User
await TranslationHandler.get_for_guild(bot, guild_id, path)     # Guild
await TranslationHandler.get_all_translations(path, langs)      # Multi
```

### Utility Methods

```python
await TranslationHandler.load_messages(lang, force_reload)      # Load
await TranslationHandler.clear_cache(lang)                      # Clear cache
TranslationHandler.get_cache_stats()                            # Cache stats
TranslationHandler.get_available_languages()                    # Available languages
await TranslationHandler.validate_translations(lang)            # Validation
```

## 📄 License

Use it as you want! 🚀

## 🤝 Contributing

Improvements welcome! Features:
- [ ] Hot-reload without force_reload
- [ ] JSON support in addition to YAML
- [ ] Pluralization support
- [ ] Context-based translations

---

Made with ❤️ for the Discord bot community

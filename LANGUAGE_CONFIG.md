# Language Configuration

This project now supports multiple languages. Currently supported: **English** and **Hungarian**.

## How to Configure

Add the following to your `.env` file:

```bash
# Language Configuration
# Options: english, hungarian
LANGUAGE=english
```

## Changing Languages

Simply update the `LANGUAGE` variable in your `.env` file:

- For English: `LANGUAGE=english`
- For Hungarian: `LANGUAGE=hungarian`

The agent will automatically use the appropriate language for:
- Greeting messages
- System prompts sent to AI models (Claude, Gemini, Ollama)
- Reminder responses
- Contact information responses
- Error messages
- All user-facing text

## How It Works

1. The `translations.py` file contains all text in both languages
2. The `config.py` reads the `LANGUAGE` environment variable
3. All components (conversation manager, sub-agents, AI clients) use the `get_text()` function to fetch the appropriate translation

## Adding New Languages

To add a new language:

1. Edit `translations.py`
2. Add a new language key to the `TRANSLATIONS` dictionary
3. Provide translations for all existing keys
4. Set `LANGUAGE` in `.env` to your new language code

Example:
```python
TRANSLATIONS = {
    'english': {...},
    'hungarian': {...},
    'spanish': {  # New language
        'greeting': "hola amigo como puedo ayudarte",
        ...
    }
}
```

## Note

The language setting applies to the AI assistant's responses and system messages. User input can be in any language - the AI models are multilingual and will respond appropriately based on the conversation context.


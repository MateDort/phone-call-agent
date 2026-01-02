# Migration Guide: New Agentic System with Gemini Live Audio

## What Changed?

This is a complete rebuild of the phone call agent with three major upgrades:

### 1. **Gemini Native Audio** (Replaces ElevenLabs)
- **Before**: Separate TTS (ElevenLabs) + LLM (Claude/Gemini/Ollama)
- **After**: Gemini 2.5 Flash with native audio I/O
- **Benefits**: 
  - Lower latency (no separate TTS calls)
  - Single API for both voice and intelligence
  - Natural conversation flow with interruptions

### 2. **Google Search Integration**
- **Before**: Agent had no access to real-time information
- **After**: Built-in Google Search automatically used when needed
- **Benefits**:
  - Answers questions about current events
  - Looks up real-time information (weather, news, etc.)
  - No code needed - Gemini decides when to search

### 3. **Agentic Hierarchy with Function Calling**
- **Before**: Single monolithic agent
- **After**: Main agent + specialized sub-agents
- **Benefits**:
  - Calendar management
  - Customer database lookups
  - Knowledge base searches
  - Calculations
  - Easily extensible with new agents

## Architecture Comparison

### Old Architecture:
```
Phone Call (Twilio)
    ↓
Webhooks (Flask)
    ↓
Speech-to-Text (Twilio)
    ↓
LLM (Claude/Gemini/Ollama)
    ↓
Text-to-Speech (ElevenLabs)
    ↓
Audio Response
```

### New Architecture:
```
Phone Call (Twilio)
    ↓
Media Streams (WebSocket)
    ↓
Gemini Live Audio (Native Voice + LLM)
    ├─> Google Search (automatic)
    └─> Function Calls
        ├─> Calendar Agent
        ├─> Data Lookup Agent
        ├─> Customer Service Agent
        ├─> Notification Agent
        └─> Calculator Agent
```

## File Changes

### New Files:
- `gemini_live_client.py` - Gemini Live Audio client with function calling
- `sub_agents.py` - Sub-agent implementations
- `twilio_media_streams.py` - WebSocket integration for real-time audio
- `main_new.py` - New main entry point
- `requirements_new.txt` - Updated dependencies

### Modified Files:
- `config.py` - Added Gemini-specific configuration
- `env_new.example` - Updated environment variables

### Deprecated Files:
- `elevenlabs_client.py` - No longer needed (voice handled by Gemini)
- `speech_handler.py` - No longer needed
- `claude_client.py` - No longer needed (Gemini is primary LLM)
- `ollama_client.py` - No longer needed
- `conversation_manager.py` - Logic moved to Gemini Live

## Setup Instructions

### 1. Install New Dependencies

```bash
pip install -r requirements_new.txt
```

### 2. Update Environment Variables

Copy the new example:
```bash
cp env_new.example .env
```

Update your `.env` file:
```env
# Required: Get from console.cloud.google.com
GEMINI_API_KEY=your_gemini_api_key

# Required: Your Twilio credentials
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
TARGET_PHONE_NUMBER=+1234567890

# Required: Your public webhook URL (use ngrok for testing)
WEBHOOK_BASE_URL=https://your-url.ngrok.io
WEBHOOK_PORT=5000
WEBSOCKET_PORT=5001
```

### 3. Setup ngrok

The new system requires **two tunnels** (HTTP + WebSocket):

```bash
# Terminal 1: HTTP tunnel for webhooks
ngrok http 5000

# Terminal 2: WebSocket tunnel for Media Streams
ngrok http 5001
```

Update your `.env`:
```env
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

### 4. Run the New System

```bash
python main_new.py
```

## Key Differences

### Voice Configuration

**Old System:**
```python
# Required separate ElevenLabs API key
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=EXAVIT9mxAsU4AKpD7Kx
```

**New System:**
```python
# Just specify voice name
GEMINI_VOICE=Kore  # Options: Kore, Puck, Charon
```

### Adding Custom Functions

**Old System:**
- Hard to extend
- Required modifying conversation logic

**New System:**
- Easy to add new sub-agents
- Just register a function declaration + handler

Example:
```python
# In sub_agents.py, create your agent:
class WeatherAgent(SubAgent):
    async def execute(self, args):
        location = args.get("location")
        # Call weather API...
        return f"Weather in {location}: Sunny, 72°F"

# In main_new.py, register it:
weather_declaration = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "location": {"type": "STRING"}
        },
        "required": ["location"]
    }
}

gemini_client.register_function(weather_declaration, weather_agent.execute)
```

### Google Search

**Old System:**
- No search capability
- Agent couldn't answer current events

**New System:**
- Automatic Google Search
- Just add to config:
```python
tools = [{'google_search': {}}]
```

Gemini automatically searches when it needs current information!

## Testing

### Test Google Search:
Call the agent and ask:
- "What's the weather in New York?"
- "What are the latest AI news?"
- "Who won the game last night?"

### Test Function Calling:
Call the agent and say:
- "Schedule a meeting for tomorrow at 2pm" → Calls `manage_calendar`
- "What are your business hours?" → Calls `lookup_information`
- "Calculate 25 times 4" → Calls `calculate`

### Test Natural Conversation:
The agent now handles interruptions and natural speech patterns better than before.

## Troubleshooting

### WebSocket Connection Issues:
- Make sure both HTTP and WebSocket tunnels are running
- Check that `WEBSOCKET_PORT` is correct in `.env`
- Verify ngrok URLs are accessible

### Audio Quality Issues:
- Twilio uses μ-law audio at 8kHz
- Gemini expects PCM audio
- If audio is garbled, may need to implement audio conversion in `AudioConverter` class

### Function Not Called:
- Check function declaration format
- Verify handler is registered
- Look at logs to see if Gemini attempted the call

## Rollback Plan

If you need to rollback to the old system:

```bash
# Use old main.py
python main.py  # Still available

# Or restore old requirements
pip install -r requirements.txt
```

## Benefits Summary

| Feature | Old System | New System |
|---------|-----------|-----------|
| **Latency** | High (separate TTS calls) | Low (native audio) |
| **Voice Quality** | Good (ElevenLabs) | Excellent (Gemini native) |
| **Real-time Info** | ❌ No search | ✅ Google Search |
| **Extensibility** | ❌ Hard to extend | ✅ Easy sub-agents |
| **Interruptions** | ❌ Not supported | ✅ Natural flow |
| **Cost** | $$$ (ElevenLabs + LLM) | $$ (Single API) |
| **Maintenance** | Multiple services | Single service |

## Next Steps

1. **Test thoroughly** with real phone calls
2. **Add your own sub-agents** for specific business logic
3. **Tune the system prompt** in `main_new.py` for your use case
4. **Monitor performance** and adjust audio settings if needed
5. **Deploy to production** with proper ngrok alternatives (Twilio Functions, etc.)

## Questions?

Check the original TARS system documentation for more details on:
- Function calling patterns
- Audio configuration
- Sub-agent design patterns


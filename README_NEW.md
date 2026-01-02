# Phone Call Agent with Gemini Live Audio & Agentic System

A sophisticated phone call agent powered by Google's Gemini 2.5 Flash with native audio capabilities, Google Search integration, and an agentic hierarchy system for specialized tasks.

## 🌟 Features

### 🎙️ Native Voice Conversations
- **Gemini 2.5 Flash Native Audio** - No separate TTS/STT needed
- **Low latency** real-time audio streaming
- **Natural interruptions** and conversation flow
- **High-quality voice** (Kore, Puck, or Charon)

### 🔍 Google Search Integration
- **Automatic search** for current events, weather, news
- **Real-time information** without any code
- Gemini decides when to search automatically

### 🤖 Agentic Hierarchy System
- **Main Agent** coordinates conversation
- **Sub-Agents** handle specialized tasks:
  - 📅 **Calendar Agent** - Schedule, list, delete events
  - 📊 **Data Lookup Agent** - Search knowledge base
  - 👤 **Customer Service Agent** - Customer/order lookups
  - 🔔 **Notification Agent** - Send alerts and reminders
  - 🧮 **Calculator Agent** - Mathematical operations

### 📞 Twilio Integration
- **Media Streams** for real-time audio via WebSocket
- **Inbound and outbound** calls supported
- **Call status tracking** and management

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│  Phone Call (Twilio)                        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Media Streams (WebSocket)                  │
│  - Real-time audio bidirectional            │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│  Gemini Live Audio (Main Agent)             │
│  - Native voice I/O                         │
│  - Conversation management                  │
│  - Function calling coordinator             │
└───┬─────────────────────────────────────────┘
    │
    ├─> 🔍 Google Search (Built-in)
    │   └─> Automatic real-time information
    │
    └─> 🛠️ Function Calls
        ├─> 📅 Calendar Agent
        ├─> 📊 Data Lookup Agent
        ├─> 👤 Customer Service Agent
        ├─> 🔔 Notification Agent
        └─> 🧮 Calculator Agent
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Twilio account with phone number
- Google Gemini API key
- ngrok (for local development)

### Installation

1. **Clone and navigate to the project:**
```bash
cd phone-call-agent
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements_new.txt
```

4. **Configure environment:**
```bash
cp env_new.example .env
# Edit .env with your credentials
```

### Configuration

Edit `.env` file:

```env
# Twilio (Required)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TARGET_PHONE_NUMBER=+1234567890

# Webhook URLs (Required)
WEBHOOK_BASE_URL=https://your-url.ngrok.io
WEBHOOK_PORT=5000
WEBSOCKET_PORT=5001

# Gemini (Required)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_VOICE=Kore  # Options: Kore, Puck, Charon

# Optional
AUTO_CALL=false  # Set true to auto-dial on startup
```

### Setup ngrok

You need **two tunnels** (one for HTTP webhooks, one for WebSocket):

**Terminal 1:**
```bash
ngrok http 5000
```

**Terminal 2:**
```bash
ngrok http 5001
```

Copy the HTTPS URL from Terminal 1 to `WEBHOOK_BASE_URL` in your `.env` file.

### Run

```bash
python main_new.py
```

You should see:
```
============================================================
Phone Call Agent with Gemini Live Audio
Features: Native Voice, Google Search, Agentic System
============================================================
INFO - Registering sub-agents...
INFO - Registered function: manage_calendar -> calendar_agent
INFO - Starting webhook server on port 5000
INFO - Starting Media Streams WebSocket server on 0.0.0.0:5001
INFO - Ready to receive calls!
```

### Make a Call

**Option 1: Auto-dial**
Set `AUTO_CALL=true` in `.env` and restart

**Option 2: Call manually**
Call your Twilio phone number from your phone

**Option 3: Use Twilio Console**
Use Twilio's console to initiate a call

## 💬 Example Conversations

### Google Search Integration
```
You: "What's the weather in San Francisco?"
Agent: "Let me check... Currently in San Francisco, it's 62°F and partly cloudy."

You: "Who won the Super Bowl last year?"
Agent: "The Kansas City Chiefs won Super Bowl LVIII in 2024."
```

### Calendar Management
```
You: "Schedule a meeting for tomorrow at 2pm"
Agent: *calls manage_calendar function*
Agent: "I've scheduled a meeting for tomorrow at 2pm."

You: "What's on my calendar?"
Agent: *calls manage_calendar function*
Agent: "You have one event: Meeting on 2025-01-02 at 14:00."
```

### Data Lookup
```
You: "What are your business hours?"
Agent: *calls lookup_information function*
Agent: "Our business hours are Monday through Friday, 9 AM to 5 PM Eastern."

You: "What's your return policy?"
Agent: *calls lookup_information function*
Agent: "We offer a 30-day money back guarantee on all products."
```

### Customer Service
```
You: "Can you look up my account?"
Agent: "Sure, what's your phone number?"
You: "+14049525557"
Agent: *calls customer_service function*
Agent: "I found your account, John Doe. You're an active customer with 2 orders."
```

### Calculations
```
You: "What's 25 times 48?"
Agent: *calls calculate function*
Agent: "25 times 48 equals 1,200."
```

## 🔧 Customization

### Add Your Own Sub-Agent

1. **Create agent class in `sub_agents.py`:**
```python
class WeatherAgent(SubAgent):
    def __init__(self):
        super().__init__(
            name="weather_agent",
            description="Gets detailed weather information"
        )
    
    async def execute(self, args: Dict[str, Any]) -> str:
        location = args.get("location")
        # Call your weather API here
        return f"Weather in {location}: Sunny, 72°F"
```

2. **Add function declaration:**
```python
def get_function_declarations():
    return [
        # ... existing declarations ...
        {
            "name": "get_weather",
            "description": "Get detailed weather information for a location",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "location": {
                        "type": "STRING",
                        "description": "City name or location"
                    }
                },
                "required": ["location"]
            }
        }
    ]
```

3. **Register in `main_new.py`:**
```python
agents = get_all_agents()
agents["weather"] = WeatherAgent()

function_map = {
    # ... existing mappings ...
    "get_weather": agents["weather"],
}
```

### Customize System Prompt

Edit `main_new.py`:
```python
system_instruction = """You are a helpful AI assistant on a phone call.

[Your custom instructions here]

Keep responses concise for phone conversations."""
```

### Change Voice

In `.env`:
```env
GEMINI_VOICE=Puck  # Options: Kore, Puck, Charon
```

## 📁 Project Structure

```
phone-call-agent/
├── main_new.py                 # Main entry point
├── gemini_live_client.py       # Gemini Live Audio client
├── sub_agents.py               # Sub-agent implementations
├── twilio_media_streams.py     # Twilio WebSocket integration
├── config.py                   # Configuration management
├── requirements_new.txt        # Dependencies
├── env_new.example             # Environment template
├── README_NEW.md               # This file
└── MIGRATION_GUIDE.md          # Migration from old system
```

## 🐛 Troubleshooting

### "Not connected to Gemini Live"
- Check your `GEMINI_API_KEY` is valid
- Ensure you have access to the beta API
- Verify internet connection

### Audio is garbled
- Check ngrok tunnels are running
- Verify WebSocket connection (check logs)
- May need audio format conversion (see `AudioConverter` in `twilio_media_streams.py`)

### Function not being called
- Check function declaration format
- Verify the function is registered (check startup logs)
- Test with explicit requests: "Use the calendar function to schedule..."

### WebSocket connection drops
- ngrok tunnels may have timed out - restart them
- Check firewall/network settings
- Verify `WEBSOCKET_PORT` is accessible

## 📊 Comparison with Old System

| Feature | Old System | New System |
|---------|-----------|-----------|
| Voice | ElevenLabs (separate API) | Gemini Native Audio |
| LLM | Claude/Gemini/Ollama | Gemini 2.5 Flash |
| Search | ❌ None | ✅ Google Search |
| Function Calling | ❌ Not supported | ✅ Full support |
| Latency | ~2-3 seconds | ~500ms |
| Interruptions | ❌ No | ✅ Yes |
| Cost | $$$ (multiple APIs) | $$ (single API) |
| Extensibility | ❌ Difficult | ✅ Easy |

## 🔐 Security Notes

- Never commit `.env` file
- Keep API keys secure
- Use HTTPS for webhooks in production
- Implement authentication for production deployments
- Consider rate limiting for function calls

## 📝 License

[Your license here]

## 🤝 Contributing

[Your contribution guidelines]

## 📮 Support

For issues or questions:
- Check the `MIGRATION_GUIDE.md` for common problems
- Review Twilio Media Streams documentation
- Check Gemini API documentation

## 🎯 Next Steps

1. ✅ Test with real phone calls
2. ✅ Add your own sub-agents
3. ✅ Customize system prompt for your use case
4. ✅ Deploy to production (replace ngrok with proper hosting)
5. ✅ Monitor and optimize performance

## 🔗 Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Twilio Media Streams](https://www.twilio.com/docs/voice/twiml/stream)
- [Function Calling Guide](https://ai.google.dev/docs/function_calling)
- [TARS System Reference](https://github.com/yourusername/tars) (original inspiration)

---

Built with ❤️ using Gemini 2.5 Flash Native Audio, inspired by the TARS agentic system.


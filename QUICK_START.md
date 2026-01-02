# Quick Start Guide - New Agentic System

This is the fastest way to get the new Gemini Live Audio system running.

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Twilio account with phone number
- [ ] Google Gemini API key (from ai.google.dev)
- [ ] ngrok installed

## 5-Minute Setup

### Step 1: Install Dependencies (2 min)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements_new.txt
```

### Step 2: Configure Environment (2 min)

```bash
# Copy template
cp env_new.example .env

# Edit .env file with your credentials
nano .env  # or use any text editor
```

**Minimum required configuration:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TARGET_PHONE_NUMBER=+1234567890
WEBHOOK_BASE_URL=http://localhost:5000
```

### Step 3: Start ngrok (1 min)

Open **two terminals** and run:

**Terminal 1:**
```bash
ngrok http 5000
```

**Terminal 2:**
```bash
ngrok http 5001
```

Copy the HTTPS URL from Terminal 1 (looks like `https://abc123.ngrok.io`) and update your `.env`:
```env
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

### Step 4: Run the Agent

**Easy way:**
```bash
./start.sh
```

**Manual way:**
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
INFO - Registered 5 sub-agents
INFO - Starting webhook server on port 5000
INFO - WebSocket server running on ws://0.0.0.0:5001
INFO - Ready to receive calls!
```

### Step 5: Test It!

**Option A: Call your Twilio number**
```
Call your TWILIO_PHONE_NUMBER from any phone
```

**Option B: Auto-dial (set AUTO_CALL=true in .env)**
```
The agent will automatically call TARGET_PHONE_NUMBER on startup
```

## Test Conversations

Try these to test different features:

### Test Google Search:
- "What's the weather in New York?"
- "What are the latest AI news?"
- "Who is the president of France?"

### Test Calendar:
- "Schedule a meeting tomorrow at 2pm"
- "What's on my calendar?"
- "Delete the meeting"

### Test Knowledge Base:
- "What are your business hours?"
- "What's your return policy?"
- "How do I contact support?"

### Test Calculations:
- "What's 25 times 48?"
- "Calculate 100 plus 200"

### Test Customer Service:
- "Look up customer +14049525557"
- "What's the status of order ORDER-123?"

## Common Issues

### "Cannot connect to Gemini Live"
```bash
# Check your API key
echo $GEMINI_API_KEY

# Verify it's in .env
cat .env | grep GEMINI_API_KEY
```

### "WebSocket connection failed"
```bash
# Make sure both ngrok tunnels are running
# Check that ports 5000 and 5001 aren't in use

# On Mac/Linux:
lsof -i :5000
lsof -i :5001

# On Windows:
netstat -ano | findstr :5000
netstat -ano | findstr :5001
```

### "Audio is garbled"
This is likely an audio format issue. The system expects:
- Twilio: μ-law audio at 8kHz
- Gemini: PCM audio

You may need to implement audio conversion in `AudioConverter` class.

### "Function not being called"
Check the logs to see if Gemini is attempting to call the function:
```
INFO - Function call: manage_calendar({'action': 'list'})
```

If you see the log, the function was called. If not, the system prompt may need adjustment.

## Architecture Overview

```
Your Phone
    ↓
Twilio Phone Number
    ↓
ngrok (5000) → Flask Webhooks
    ↓
ngrok (5001) → WebSocket Media Streams
    ↓
Gemini Live Audio (Main Agent)
    ├─> Google Search (automatic)
    └─> Sub-Agents (function calling)
        ├─> Calendar
        ├─> Data Lookup
        ├─> Customer Service
        ├─> Notifications
        └─> Calculator
```

## What's Different from Old System?

| Feature | Old System | New System |
|---------|-----------|-----------|
| Files to run | `python main.py` | `python main_new.py` |
| Voice API | ElevenLabs | Gemini Native |
| LLM API | Claude/Ollama | Gemini |
| Search | None | Google Search |
| Functions | None | 5+ sub-agents |
| Latency | 2-3 seconds | ~500ms |

## Next Steps

1. **Read the full documentation:**
   - `README_NEW.md` - Complete guide
   - `MIGRATION_GUIDE.md` - Detailed migration info

2. **Customize for your use case:**
   - Add your own sub-agents in `sub_agents.py`
   - Modify system prompt in `main_new.py`
   - Update knowledge base with your data

3. **Deploy to production:**
   - Replace ngrok with permanent hosting
   - Add authentication and rate limiting
   - Monitor costs and performance

## Getting Help

- **Logs**: Check terminal output for detailed error messages
- **Documentation**: Read `README_NEW.md` and `MIGRATION_GUIDE.md`
- **Twilio Dashboard**: Check call logs and debugger
- **Gemini Console**: Monitor API usage and quota

## Cost Estimates

Based on typical usage:

- **Gemini API**: ~$0.02 per minute of conversation
- **Twilio Voice**: ~$0.01-0.02 per minute (varies by country)
- **Total**: ~$0.03-0.04 per minute

Much cheaper than the old system (ElevenLabs + Claude)!

## Success! 🎉

If you can:
- ✅ Make/receive calls
- ✅ Have natural conversations
- ✅ Get answers about current events (Google Search working)
- ✅ Schedule calendar events (function calling working)

Then you're all set! The new system is running perfectly.

---

**Questions?** Check `README_NEW.md` or `MIGRATION_GUIDE.md` for more details.


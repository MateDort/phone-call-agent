# Phone Call Agent

An AI-powered phone call agent that can initiate calls and have natural conversations using local Ollama LLM and macOS voice synthesis.

## Features

- Makes outbound phone calls via Twilio
- Uses local Ollama LLM (llama2) for conversation
- Text-to-speech using macOS built-in voice
- Real-time speech recognition via Twilio
- Maintains conversation context

## Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
   - Install from [ollama.ai](https://ollama.ai)
   - Pull the llama2 model: `ollama pull llama2`
3. **Twilio Account** with:
   - Account SID
   - Auth Token
   - A phone number (configured in project: +1 (445) 234-4131)
4. **macOS** (for `say` command and `afconvert`)

## Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd phone-call-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   ```

4. **Set up ngrok for webhooks (local development):**
   
   Twilio needs a publicly accessible URL for webhooks. For local development:
   
   ```bash
   # Install ngrok: https://ngrok.com/download
   # Start ngrok tunnel
   ngrok http 5000
   ```
   
   Copy the ngrok URL (e.g., `https://abc123.ngrok.io`) and update `.env`:
   ```
   WEBHOOK_BASE_URL=https://abc123.ngrok.io
   ```

5. **Ensure Ollama is running:**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # If not running, start it (usually runs automatically after installation)
   ```

## Usage

1. **Start the agent:**
   ```bash
   python main.py
   ```

2. The agent will:
   - Start the webhook server
   - Initiate a call to the target number (404 952 5557)
   - Say "hey friend how can i help you"
   - Listen for your response and continue the conversation

3. **Stop the agent:**
   - Press `Ctrl+C` to gracefully shutdown

## Configuration

Edit `.env` file to customize:

- `TARGET_PHONE_NUMBER`: Phone number to call (default: +14049525557)
- `OLLAMA_MODEL`: Ollama model to use (default: llama2)
- `WEBHOOK_PORT`: Port for webhook server (default: 5000)

## Project Structure

```
phone-call-agent/
├── main.py                 # Entry point
├── config.py              # Configuration management
├── twilio_handler.py       # Twilio integration
├── speech_handler.py      # Text-to-speech
├── ollama_client.py        # Ollama LLM client
├── conversation_manager.py # Conversation state
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

## How It Works

1. **Call Initiation**: `main.py` starts Flask server and initiates Twilio call
2. **Webhook Handling**: Twilio sends webhook to `/webhook/voice` when call connects
3. **Greeting**: Agent generates greeting audio using macOS `say` command
4. **Speech Input**: Twilio's `<Gather>` verb captures user speech
5. **Processing**: Speech → Text → Ollama LLM → Response text
6. **Response**: Response text → macOS `say` → Audio → Twilio playback
7. **Loop**: Continues conversation until call ends

## Troubleshooting

**Cannot connect to Ollama:**
- Ensure Ollama is running: `ollama list`
- Check OLLAMA_BASE_URL in `.env`

**Twilio webhook errors:**
- Verify ngrok is running and WEBHOOK_BASE_URL is correct
- Check Twilio console for webhook logs

**Audio generation issues:**
- Ensure macOS `say` command works: `say "test"`
- Check `afconvert` is available (built into macOS)

**Call not connecting:**
- Verify Twilio credentials in `.env`
- Check phone numbers are in E.164 format (+1XXXXXXXXXX)
- Review Twilio console for call logs

## License

MIT


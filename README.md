# Elderly Care Phone Agent

A compassionate AI phone assistant for elderly care, powered by Google Gemini Live Audio with natural voice conversations, smart reminders, family contact management, and multilingual support.

## 🌟 Features

### 🔔 Smart Medication Reminders
- **Automatic phone calls** when reminders are due
- **Recurring reminders** - daily, weekly, or specific days
- **Easy management** - natural language commands
- **Local storage** - all reminders saved safely
- **During call announcements** - mentions reminders naturally if already on the phone

**Examples:**
- "Remind me to take my pill every day at 3pm"
- "What reminders do I have?"
- "Delete my 8am reminder"
- "Change the 9am reminder to 10am"

### 👥 Family & Friends Contacts
- Store family and friends information
- Quick access to phone numbers and birthdays
- **Birthday reminders** - "Today is Helen's birthday!"
- Easy lookup by name

**Currently stored:**
- **Helen Stadler** - Girlfriend
  - Phone: 404-953-5533
  - Birthday: August 27, 2004

### 📖 Personal Biography
The assistant knows all about Máté:
- Life story and background (Hungary → USA)
- Swimming achievements and competitive career
- Education (Life University, graduating 2026)
- Goals and aspirations (designer-inventor)
- Values and interests

### 🌍 Multilingual Support
- **English** (default)
- **Hungarian** (magyar)
- **Spanish** (español)
- Easy switching: "Switch to Hungarian" or "Váltson magyarra"

### 🔍 Google Search
- Current weather, news, sports scores
- Real-time information automatically retrieved

### 🎤 Natural Voice Conversations
- **Low latency** (~500ms response time)
- **Natural interruptions** - just like talking to a person
- **Warm and friendly** - conversational and supportive
- **Clear speech** - easy to understand

## 🚀 Quick Setup

### Prerequisites
- Python 3.9+
- Twilio account with phone number
- Google Gemini API key
- ngrok (for local development)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your credentials
```

**Required in `.env`:**
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

# Language (Optional)
LANGUAGE=en  # Options: en, hu, es

# Optional
AUTO_CALL=false  # Set true to auto-dial on startup
```

3. **Setup database:**
```bash
python setup_elderly_db.py
```

This initializes the local database with:
- User bio (Máté's information)
- Contacts (Helen Stadler)
- Reminder system

4. **Start ngrok (one terminal with the script):**
```bash
./start_ngrok.sh
```

This starts both required tunnels (ports 5000 and 5001) in one session.

Copy the HTTPS URL from the output and update `WEBHOOK_BASE_URL` in your `.env` file.

5. **Run the agent:**
```bash
python main_elderly.py
# or
./start_elderly.sh
```

## 📞 How It Works

### Automatic Reminder Calls

```
Reminder Time Arrives
    ↓
System Checks if User is on Phone
    ↓
If NOT on phone:
    ↓
System Makes Automatic Call
    ↓
User Answers
    ↓
AI: "Hi Máté! You have a reminder: take your afternoon medication"
    ↓
Natural conversation continues

If ALREADY on phone:
    ↓
AI Mentions Naturally: "By the way, it's time to take your medication"
```

## 💬 Example Conversations

### Setting Reminders
```
User: "Remind me to take my pill every day at 3pm"
AI: "Reminder saved: take your pill at 3:00 PM every day"

User: "What reminders do I have?"
AI: "Your reminders:
     - Take afternoon medication at 3:00 PM every day
     - Doctor appointment at 8:00 AM on January 15"

User: "Delete my 8am reminder"
AI: "Deleted reminder: Doctor appointment"
```

### Looking Up Contacts
```
User: "What's Helen's phone number?"
AI: "Helen Stadler's phone number is 404-953-5533"

User: "When is Helen's birthday?"
AI: "Helen's birthday is August 27, 2004"
```

### Learning About User
```
User: "Tell me about my background"
AI: "You were born in 2003 in Dunaújváros, raised in Kisapostag, Hungary. 
     You started swimming at age 3 and became a top competitor in the U.S."

User: "What are my goals?"
AI: "Your goals include becoming an iconic designer-inventor and achieving 
     financial freedom by 30."
```

### Language Switching
```
User: "Switch to Hungarian"
AI: "Rendben, magyar nyelvre váltok."

User: "Emlékeztess, hogy vegyek be gyógyszert minden nap délután 3-kor"
AI: "Emlékeztető mentve: vegyek be gyógyszert 15:00-kor minden nap"

User: "Switch to English"
AI: "Switching to English."
```

## 🗂️ Database Structure

All data is stored locally in `elderly_care.db`:

### Reminders Table
- ID, title, datetime, recurrence pattern
- Days of week (for weekly recurring)
- Active status, last triggered time

### Contacts Table
- Name, relation, phone, birthday, notes

### User Bio Table
- Key-value pairs for biographical information

## 🔧 Customization

### Add More Contacts

```python
from database import Database
db = Database("elderly_care.db")

db.add_contact(
    name="Dr. Smith",
    relation="Doctor",
    phone="555-1234",
    birthday="1970-05-15",
    notes="Family physician"
)
```

### Modify User Bio

```python
db.set_bio("favorite_food", "Hungarian goulash")
db.set_bio("hometown", "Kisapostag, Hungary")
```

### Add New Language

1. Add translations to `translations.py`
2. Update `Config.SUPPORTED_LANGUAGES` in `config.py`
3. Restart the agent

## 🎯 System Architecture

```
┌─────────────────────────────────────────┐
│  Reminder Checker (Background)          │
│  - Checks every 60 seconds              │
│  - Triggers calls when reminders due    │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  Phone Call (Twilio)                    │
│  - Inbound or auto-triggered            │
└────────┬────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  Gemini Live Audio (Main Agent)         │
│  - Natural voice conversations          │
│  - Google Search for current info       │
│  - Multilingual support                 │
│  - Function calling for actions         │
└────────┬────────────────────────────────┘
         │
         ├─> 🔔 Reminder Agent (Local DB)
         ├─> 👥 Contacts Agent (Local DB)
         ├─> 📖 User Bio Agent (Local DB)
         ├─> 🔔 Notification Agent
         ├─> 🕐 Time Utility
         └─> 🔍 Google Search (Built-in)
```

## 📂 Project Structure

```
phone-call-agent/
├── main_elderly.py             # Main entry point
├── config.py                   # Configuration management
├── database.py                 # SQLite database operations
├── gemini_live_client.py       # Gemini Live Audio client
├── sub_agents_elderly.py       # Specialized sub-agents
├── reminder_checker.py         # Background reminder system
├── translations.py             # Multilingual support
├── twilio_media_streams.py     # Twilio WebSocket integration
├── setup_elderly_db.py         # Database initialization
├── start_elderly.sh            # Quick startup script
├── start_ngrok.sh              # ngrok tunnel manager
├── requirements_new.txt        # Python dependencies
├── env_new.example             # Environment template
├── elderly_care.db             # Local database (created on setup)
├── ELDERLY_CARE_README.md      # Detailed documentation
├── ELDERLY_CARE_SUMMARY.md     # Feature summary
└── project.md                  # Project notes
```

## 🔒 Privacy & Security

- **All data stored locally** on your machine
- **No cloud storage** for personal information
- **Database file:** `elderly_care.db` in project directory
- **Easy backup** - just copy the .db file

## 🐛 Troubleshooting

### Reminder Not Triggering?
- Check the time is correct in the database
- Ensure the agent is running
- Check logs for errors

### Call Quality Issues?
- Verify ngrok tunnels are running
- Check internet connection
- Review Twilio call logs

### Can't Find Contact?
- Try searching by first name only
- Check spelling in database
- Use `python setup_elderly_db.py` to reset

### Language Not Switching?
- Ensure translations exist in `translations.py`
- Check `LANGUAGE` setting in config
- Restart the agent after changes

## 💡 Tips for Best Experience

### For Clear Communication
- Speak naturally - the AI understands conversational language
- Be specific with times: "3pm" rather than "afternoon"
- For reminders, mention "every day" or "daily" for recurring

### For Reminders
- Set them ahead of time for best results
- Use consistent times (e.g., always 3pm for medication)
- List your reminders regularly to stay organized

### For Contacts
- Add important phone numbers (doctor, family, friends)
- Include birthdays so the AI can remind you
- Update notes with helpful information

## 📊 System Requirements

- **Python:** 3.9 or higher
- **Internet:** Stable connection required
- **RAM:** 512MB minimum
- **Storage:** 100MB for code + database

## 💰 Cost Estimates

Based on typical usage:

- **Gemini API:** ~$0.02 per minute of conversation
- **Twilio Voice:** ~$0.01-0.02 per minute
- **Total:** ~$0.03-0.04 per minute

## 🎉 What Makes This Special

- **Designed for elderly care** - simple, warm, supportive
- **Automatic reminders** - never miss medication
- **Natural voice** - like talking to a friend
- **Local storage** - private and secure
- **Family focused** - quick access to loved ones
- **Multilingual** - speak in your preferred language
- **Low latency** - responds immediately
- **Always available** - 24/7 assistance

## 📝 Next Steps

1. ✅ Set up your reminders
2. ✅ Add your family contacts
3. ✅ Test with a phone call
4. ✅ Customize the user bio
5. ✅ Set your preferred language
6. ✅ Enjoy having a helpful AI assistant!

## 🔗 Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [Twilio Media Streams](https://www.twilio.com/docs/voice/twiml/stream)
- [Python Documentation](https://docs.python.org/3/)

## 📄 License

MIT License - Feel free to use and modify for your needs.

---

**Built with ❤️ for elderly care using Gemini 2.5 Flash Native Audio**

**Status:** ✅ Production Ready for Personal Use

For detailed feature documentation, see `ELDERLY_CARE_README.md`


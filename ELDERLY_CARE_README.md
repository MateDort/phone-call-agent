# Elderly Care Phone Agent

A compassionate AI phone assistant for elderly care, powered by Google Gemini Live Audio with natural voice conversations, smart reminders, and family contact management.

## 🌟 Features for Elderly Care

### 🔔 Smart Medication Reminders
- **Automatic phone calls** when reminders are due
- **Recurring reminders** - daily, weekly, or specific days
- **Easy management** - "remind me to take my pill every day at 3pm"
- **Local storage** - all reminders saved safely
- **During call announcements** - if you're already on the phone, the assistant mentions the reminder naturally

**Examples:**
- "Remind me to take my pill every day at 3pm"
- "Remind me about my doctor appointment tomorrow at 8am"
- "What reminders do I have?"
- "Delete my 8am reminder"
- "Change the 9am reminder to 10am"

### 👥 Family & Friends Contacts
- Store family and friends information
- Quick access to phone numbers
- **Birthday reminders** - "Today is Helen's birthday!"
- Easy lookup - "What's Helen's phone number?"

**Currently stored:**
- **Helen Stadler** - Girlfriend
  - Phone: 404-953-5533
  - Birthday: August 27, 2004

### 📖 Personal Biography
The assistant knows all about Máté:
- Life story and background
- Achievements and goals
- Interests and hobbies
- Daily routine and values

**Try asking:**
- "Tell me about my background"
- "What are my goals?"
- "What do I like to do?"

### 🔍 Google Search
- Current weather
- Latest news
- Sports scores
- Any real-time information

**Examples:**
- "What's the weather today?"
- "What's happening in the news?"

### 🎤 Natural Voice Conversations
- **Low latency** - responds in ~500ms
- **Natural interruptions** - just like talking to a person
- **Warm and friendly** - conversational and supportive
- **Clear speech** - easy to understand

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp env.example .env
# Edit .env with your credentials
```

**Required in `.env`:**
```env
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
TARGET_PHONE_NUMBER=+1234567890  # Máté's phone number
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

### 3. Setup Database
```bash
python setup_elderly_db.py
```

This initializes:
- ✓ User bio (Máté's information)
- ✓ Contacts (Helen Stadler)
- ✓ Reminder system

### 4. Start ngrok (2 terminals)
```bash
# Terminal 1
ngrok http 5000

# Terminal 2
ngrok http 5001
```

### 5. Run the Agent
```bash
python main_elderly.py
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
AI Says: "Hi Máté! You have a reminder: take your afternoon medication"
    ↓
Natural conversation continues

If ALREADY on phone:
    ↓
AI Mentions Naturally: "By the way, it's time to take your medication"
```

### Example Conversations

**Setting Reminders:**
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

**Looking Up Contacts:**
```
User: "What's Helen's phone number?"
AI: "Helen Stadler
     Relation: Girlfriend
     Phone: 404-953-5533
     Birthday: August 27, 2004"

User: "When is Helen's birthday?"
AI: "Helen's birthday is August 27, 2004"

User: "Is there a birthday today?"
AI: "Today is Helen's birthday!" (if it's August 27)
```

**Learning About User:**
```
User: "Tell me about my background"
AI: "You were born in 2003 in Dunaújváros, raised in Kisapostag, Hungary. 
     You started swimming at age 3 and became a top competitor in the U.S., 
     placing 2nd nationally by 0.07 seconds. You moved to the U.S. at 19 
     to pursue bigger dreams."

User: "What are my goals?"
AI: "Your goals include becoming an iconic designer-inventor, building 
     inventions that improve lives, traveling the world in a custom van 
     while creating products, and achieving financial freedom by 30."
```

**General Questions:**
```
User: "What's the weather today?"
AI: [Uses Google Search] "Currently it's 65°F and partly cloudy"

User: "What time is it?"
AI: "It's 2:45 PM"
```

## 🗂️ Database Structure

All data is stored locally in `elderly_care.db`:

### Reminders Table
- ID, title, datetime, recurrence, days_of_week
- Active status, last triggered time
- Supports daily, weekly, and custom recurring patterns

### Contacts Table
- Name, relation, phone, birthday, notes
- Easy search by name

### User Bio Table
- Key-value pairs for biographical information
- Fully customizable

## 🔧 Customization

### Add More Contacts

Edit `setup_elderly_db.py` or use the database directly:

```python
from database import Database
db = Database("elderly_care.db")

db.add_contact(
    name="Dr. Smith",
    relation="Doctor",
    phone="555-1234",
    notes="Family physician"
)
```

### Modify User Bio

```python
db.set_bio("favorite_food", "Hungarian goulash")
db.set_bio("hometown_memory", "Swimming in Lake Balaton")
```

### Adjust Reminder Check Interval

In `reminder_checker.py`, change:
```python
self.check_interval = 60  # Check every 60 seconds
```

## 📊 How Reminders Work

### Recurring Reminders

**Daily:**
```
"Remind me to take my pill every day at 3pm"
→ Triggers every day at 3pm until deleted
```

**Weekly (Specific Days):**
```
"Remind me every Monday and Wednesday at 9am"
→ Triggers only on Mondays and Wednesdays
```

**One-Time:**
```
"Remind me about my appointment tomorrow at 2pm"
→ Triggers once, then becomes inactive
```

### Reminder Logic

1. **System checks every 60 seconds** for due reminders
2. **If user is NOT on phone:** Makes automatic outbound call
3. **If user IS on phone:** AI mentions it naturally in conversation
4. **After triggering:** Marks as triggered to avoid duplicates
5. **For recurring:** Automatically schedules next occurrence

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
│  - Function calling for actions         │
└────────┬────────────────────────────────┘
         │
         ├─> 🔔 Reminder Agent (Local DB)
         ├─> 👥 Contacts Agent (Local DB)
         ├─> 📖 User Bio Agent (Local DB)
         └─> 🔍 Google Search (Built-in)
```

## 💡 Tips for Best Experience

### For Clear Communication:
- Speak naturally - the AI understands conversational language
- Be specific with times: "3pm" rather than "afternoon"
- For reminders, mention "every day" or "daily" for recurring

### For Reminders:
- Set them ahead of time for best results
- Use consistent times (e.g., always 3pm for medication)
- List your reminders regularly to stay organized

### For Contacts:
- Add important phone numbers (doctor, family, friends)
- Include birthdays so the AI can remind you
- Update notes with helpful information

## 🔒 Privacy & Security

- **All data stored locally** on your machine
- **No cloud storage** for personal information
- **Database file:** `elderly_care.db` in project directory
- **Secure** - only accessible to the application

## 📞 Support & Troubleshooting

### Reminder Not Triggering?
- Check the time is correct in the database
- Ensure the agent is running (`python main_elderly.py`)
- Check logs for any errors

### Call Quality Issues?
- Verify ngrok tunnels are running
- Check internet connection
- Review Twilio call logs

### Can't Find Contact?
- Try searching by first name only
- Check spelling in database
- Use: `python setup_elderly_db.py` to reset

## 🎉 What Makes This Special

- **Designed for elderly care** - simple, warm, supportive
- **Automatic reminders** - never miss medication
- **Natural voice** - like talking to a friend
- **Local storage** - private and secure
- **Family focused** - quick access to loved ones
- **Low latency** - responds immediately
- **Always available** - 24/7 assistance

## 📝 Next Steps

1. ✅ Set up your reminders
2. ✅ Add your family contacts
3. ✅ Test with a phone call
4. ✅ Customize the user bio
5. ✅ Enjoy having a helpful AI assistant!

---

**Built with ❤️ for elderly care using Gemini 2.5 Flash Native Audio**

**Status:** ✅ Production Ready for Personal Use


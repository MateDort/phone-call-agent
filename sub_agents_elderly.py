"""Sub-agents for elderly care system."""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from gemini_live_client import SubAgent
from database import Database
from translations import get_text, format_text
from config import Config
import re

logger = logging.getLogger(__name__)


class ReminderAgent(SubAgent):
    """Handles reminders with local storage and automatic phone call triggers."""
    
    def __init__(self, db: Database):
        super().__init__(
            name="reminder_agent",
            description="Manages reminders with recurring support and automatic notifications"
        )
        self.db = db
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute reminder operation.
        
        Args:
            args: {
                "action": "create|list|delete|edit",
                "title": str,
                "time": str (e.g., "3pm", "tomorrow at 8am", "every day at 1pm"),
                "reminder_id": int (for delete/edit)
            }
        """
        action = args.get("action", "list")
        
        if action == "create":
            return await self._create_reminder(args)
        
        elif action == "list":
            return await self._list_reminders()
        
        elif action == "delete":
            return await self._delete_reminder(args)
        
        elif action == "edit":
            return await self._edit_reminder(args)
        
        else:
            return f"{get_text('unknown_action', Config.LANGUAGE)}: {action}"
    
    async def _create_reminder(self, args: Dict[str, Any]) -> str:
        """Create a new reminder."""
        title = args.get("title", "Reminder")
        time_str = args.get("time", "")
        
        # Parse time and recurrence
        parsed = self._parse_time(time_str)
        if not parsed:
            return f"{get_text('time_parse_error', Config.LANGUAGE)} '{time_str}'. Please try again."
        
        reminder_time = parsed['datetime']
        recurrence = parsed.get('recurrence')
        days_of_week = parsed.get('days_of_week')
        
        # Save to database
        reminder_id = self.db.add_reminder(
            title=title,
            datetime_str=reminder_time.isoformat(),
            recurrence=recurrence,
            days_of_week=days_of_week
        )
        
        logger.info(f"Created reminder {reminder_id}: {title} at {reminder_time}")
        
        # Build response
        recurrence_text = ""
        if recurrence == "daily":
            recurrence_text = f" {get_text('every_day', Config.LANGUAGE)}"
        elif recurrence == "weekly" and days_of_week:
            recurrence_text = f" {get_text('every', Config.LANGUAGE)} {days_of_week}"
        
        return f"{get_text('reminder_saved', Config.LANGUAGE)}: {title} {get_text('at', Config.LANGUAGE)} {reminder_time.strftime('%I:%M %p on %B %d, %Y')}{recurrence_text}"
    
    async def _list_reminders(self) -> str:
        """List all active reminders."""
        reminders = self.db.get_reminders(active_only=True)
        
        if not reminders:
            return get_text('no_reminders', Config.LANGUAGE)
        
        lines = [get_text('your_reminders', Config.LANGUAGE)]
        for r in reminders:
            reminder_time = datetime.fromisoformat(r['datetime'])
            time_str = reminder_time.strftime('%I:%M %p on %B %d')
            
            recurrence_text = ""
            if r['recurrence'] == 'daily':
                recurrence_text = f" ({get_text('every_day', Config.LANGUAGE)})"
            elif r['recurrence'] == 'weekly' and r['days_of_week']:
                recurrence_text = f" ({get_text('every', Config.LANGUAGE)} {r['days_of_week']})"
            
            lines.append(f"- {r['title']} {get_text('at', Config.LANGUAGE)} {time_str}{recurrence_text}")
        
        return "\n".join(lines)
    
    async def _delete_reminder(self, args: Dict[str, Any]) -> str:
        """Delete a reminder."""
        # Try to find by time or title
        time_str = args.get("time", "")
        title = args.get("title", "")
        
        reminders = self.db.get_reminders(active_only=True)
        
        # Find matching reminder
        match = None
        for r in reminders:
            reminder_time = datetime.fromisoformat(r['datetime'])
            
            # Match by time
            if time_str and time_str in reminder_time.strftime('%I %p').lower():
                match = r
                break
            
            # Match by title
            if title and title.lower() in r['title'].lower():
                match = r
                break
        
        if match:
            self.db.delete_reminder(match['id'])
            return f"{get_text('reminder_deleted', Config.LANGUAGE)}: {match['title']}"
        else:
            return get_text('couldnt_find_reminder', Config.LANGUAGE)
    
    async def _edit_reminder(self, args: Dict[str, Any]) -> str:
        """Edit a reminder."""
        old_time = args.get("old_time", "")
        new_time = args.get("new_time", "")
        
        # Find reminder by old time
        reminders = self.db.get_reminders(active_only=True)
        match = None
        
        for r in reminders:
            reminder_time = datetime.fromisoformat(r['datetime'])
            if old_time in reminder_time.strftime('%I %p').lower():
                match = r
                break
        
        if not match:
            return f"{get_text('couldnt_find_reminder', Config.LANGUAGE)} {get_text('at', Config.LANGUAGE)} {old_time}"
        
        # Parse new time
        parsed = self._parse_time(new_time)
        if not parsed:
            return f"{get_text('time_parse_error', Config.LANGUAGE)} '{new_time}'"
        
        # Update reminder
        self.db.update_reminder(
            match['id'],
            datetime=parsed['datetime'].isoformat(),
            recurrence=parsed.get('recurrence'),
            days_of_week=parsed.get('days_of_week')
        )
        
        return f"{get_text('reminder_updated', Config.LANGUAGE)} {get_text('from', Config.LANGUAGE)} {old_time} {get_text('to', Config.LANGUAGE)} {new_time}"
    
    def _parse_time(self, time_str: str) -> Dict:
        """Parse time string into datetime and recurrence.
        
        Examples:
        - "3pm" -> today at 3pm
        - "tomorrow at 8am" -> tomorrow at 8am
        - "every day at 1pm" -> daily recurring at 1pm
        - "every monday at 2pm" -> weekly on monday at 2pm
        """
        time_str = time_str.lower().strip()
        
        # Check for recurrence
        recurrence = None
        days_of_week = None
        
        if "every day" in time_str or "daily" in time_str:
            recurrence = "daily"
            time_str = re.sub(r'every day|daily', '', time_str).strip()
        
        # Check for specific days
        days_pattern = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
        if "every" in time_str and re.search(days_pattern, time_str):
            recurrence = "weekly"
            days_matches = re.findall(days_pattern, time_str)
            days_of_week = ",".join(days_matches)
            time_str = re.sub(r'every|' + days_pattern, '', time_str).strip()
        
        # Parse base time - ALWAYS use fresh current time
        now = datetime.now()
        target_time = now
        
        # Extract time with optional minutes (3pm, 8:30am, 09:14 AM, etc.)
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            
            target_time = target_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Check for relative days
        if "tomorrow" in time_str:
            target_time += timedelta(days=1)
        elif "today" not in time_str and target_time < now:
            # If time has passed today, set for tomorrow
            target_time += timedelta(days=1)
        
        return {
            'datetime': target_time,
            'recurrence': recurrence,
            'days_of_week': days_of_week
        }


class UserBioAgent(SubAgent):
    """Stores and retrieves user biographical information."""
    
    def __init__(self, db: Database):
        super().__init__(
            name="user_bio",
            description="Provides information about the user"
        )
        self.db = db
        self._init_bio()
    
    def _init_bio(self):
        """Initialize user bio with Máté's information."""
        bio_data = {
            "name": "Máté Dort",
            "birth_year": "2003",
            "birthplace": "Dunaújváros, Hungary",
            "hometown": "Kisapostag, Hungary",
            "current_location": "United States",
            "age": "21",
            "education": "Life University, graduating 2026",
            "background": "Born in 2003 in Dunaújváros, raised in Kisapostag, Hungary. Started swimming at age 3 and became a top competitor in the U.S., placing 2nd nationally by 0.07 seconds. Moved to the U.S. at 19 to pursue bigger dreams.",
            "achievements": "Built TapMate glasses at 21, competed in and placed at hackathons, became a top swimming competitor",
            "values": "Discipline, tradition, craftsmanship, personal growth, health, family relationships, and meaningful connections. Rejects social media and distractions.",
            "interests": "Design, invention, engineering, programming, swimming, marathons, languages, vintage style (50s-60s suits), reading physical books, writing on paper",
            "goals": "Become an iconic designer-inventor, build inventions that improve lives, travel the world in a custom van while creating products, achieve financial freedom by 30, explore life deeply",
            "personality": "Competitive, disciplined, curious, humorous, intelligent, deep thinker. Multi-skill creator learning fast and acting bold.",
            "routine": "Early mornings, early nights, consistent structure, trains regularly, eats clean, lives with clarity",
            "inspiration": "Steve Jobs, Ryo Lu, Tony Stark (fictional)"
        }
        
        # Check if bio already exists
        existing = self.db.get_bio()
        if not existing:
            for key, value in bio_data.items():
                self.db.set_bio(key, value)
            logger.info("User bio initialized")
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Look up user information.
        
        Args:
            args: {"query": str} - what to search for
        """
        query = args.get("query", "").lower()
        
        # Get all bio data
        bio = self.db.get_bio()
        
        # Search for relevant info
        results = []
        for key, value in bio.items():
            if query in key.lower() or query in value.lower():
                results.append(value)
        
        if results:
            return "\n".join(results[:3])  # Return top 3 matches
        else:
            # Return general overview
            return f"{bio.get('name', 'User')} - {bio.get('background', 'No information available')}"


class ContactsAgent(SubAgent):
    """Manages family and friends contact information."""
    
    def __init__(self, db: Database):
        super().__init__(
            name="contacts",
            description="Stores and retrieves family and friends information"
        )
        self.db = db
        self._init_contacts()
    
    def _init_contacts(self):
        """Initialize with Helen's contact information."""
        existing = self.db.search_contact("Helen")
        if not existing:
            self.db.add_contact(
                name="Helen Stadler",
                relation="Girlfriend",
                phone="404-953-5533",
                birthday="2004-08-27",
                notes="Birthday: August 27, 2004"
            )
            logger.info("Initial contacts added")
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Look up or manage contact information.
        
        Args:
            args: {
                "action": "lookup|list|birthday_check",
                "name": str
            }
        """
        action = args.get("action", "lookup")
        name = args.get("name", "")
        
        if action == "lookup":
            contact = self.db.search_contact(name)
            if contact:
                info = [f"{contact['name']}"]
                if contact['relation']:
                    info.append(f"{get_text('relation', Config.LANGUAGE)}: {contact['relation']}")
                if contact['phone']:
                    info.append(f"{get_text('phone', Config.LANGUAGE)}: {contact['phone']}")
                if contact['birthday']:
                    info.append(f"{get_text('birthday', Config.LANGUAGE)}: {self._format_birthday(contact['birthday'])}")
                return "\n".join(info)
            else:
                return f"{get_text('no_contact_info', Config.LANGUAGE)} {name}"
        
        elif action == "list":
            contacts = self.db.get_contacts()
            if not contacts:
                return get_text('no_contacts', Config.LANGUAGE)
            
            lines = [get_text('your_contacts', Config.LANGUAGE)]
            for c in contacts:
                lines.append(f"- {c['name']} ({c['relation']})")
            return "\n".join(lines)
        
        elif action == "birthday_check":
            # Check for upcoming birthdays
            today = datetime.now().date()
            contacts = self.db.get_contacts()
            
            upcoming = []
            for c in contacts:
                if c['birthday']:
                    bday = datetime.fromisoformat(c['birthday']).date()
                    # Check if birthday is today
                    if bday.month == today.month and bday.day == today.day:
                        upcoming.append(format_text('today_is_birthday', Config.LANGUAGE, name=c['name']))
            
            return "\n".join(upcoming) if upcoming else get_text('no_birthdays_today', Config.LANGUAGE)
        
        else:
            return f"{get_text('unknown_contact_action', Config.LANGUAGE)}: {action}"
    
    def _format_birthday(self, birthday_str: str) -> str:
        """Format birthday string nicely."""
        try:
            bday = datetime.fromisoformat(birthday_str)
            return bday.strftime("%B %d, %Y")
        except:
            return birthday_str


class NotificationAgent(SubAgent):
    """Handles notifications and can trigger phone calls."""
    
    def __init__(self):
        super().__init__(
            name="notification",
            description="Sends notifications and can trigger phone calls for important reminders"
        )
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Handle notification request.
        
        Args:
            args: {
                "message": str,
                "type": "call|message",
                "urgency": "normal|urgent"
            }
        """
        message = args.get("message", "")
        notification_type = args.get("type", "message")
        
        logger.info(f"Notification: {message} (type: {notification_type})")
        
        if notification_type == "call":
            # This would trigger a phone call in production
            return f"{get_text('phone_call_scheduled', Config.LANGUAGE)}: {message}"
        else:
            return f"{get_text('notification_sent', Config.LANGUAGE)}: {message}"


# Agent registry
def get_all_agents(db: Database) -> Dict[str, SubAgent]:
    """Get all available sub-agents.
    
    Args:
        db: Database instance
    
    Returns:
        Dictionary of agent_name -> agent_instance
    """
    return {
        "reminder": ReminderAgent(db),
        "user_bio": UserBioAgent(db),
        "contacts": ContactsAgent(db),
        "notification": NotificationAgent(),
    }


def get_function_declarations() -> list:
    """Get function declarations for all sub-agents.
    
    Returns:
        List of function declarations for Gemini
    """
    return [
        {
            "name": "manage_reminder",
            "description": "Create, list, delete, or edit reminders. Supports recurring reminders (daily, weekly). Examples: 'remind me to take my pill every day at 3pm', 'what reminders do I have', 'delete my 8am reminder', 'change 9am reminder to 10am'",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: create, list, delete, or edit"
                    },
                    "title": {
                        "type": "STRING",
                        "description": "Reminder description (e.g., 'take my pill')"
                    },
                    "time": {
                        "type": "STRING",
                        "description": "When to remind: '3pm', 'tomorrow at 8am', 'every day at 1pm', 'every monday at 2pm'"
                    },
                    "old_time": {
                        "type": "STRING",
                        "description": "For edit: the current time of the reminder"
                    },
                    "new_time": {
                        "type": "STRING",
                        "description": "For edit: the new time for the reminder"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "lookup_user_info",
            "description": "Get information about Máté - his background, goals, interests, achievements, etc.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "What information to look up (e.g., 'background', 'goals', 'interests')"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "lookup_contact",
            "description": "Look up family and friends contact information including phone numbers, birthdays, and relationships. Can also check for birthdays today.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: lookup (find specific contact), list (all contacts), or birthday_check (check today's birthdays)"
                    },
                    "name": {
                        "type": "STRING",
                        "description": "Contact name to look up"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "send_notification",
            "description": "Send a notification or trigger a phone call",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "message": {
                        "type": "STRING",
                        "description": "Notification message"
                    },
                    "type": {
                        "type": "STRING",
                        "description": "Type: 'call' (phone call) or 'message' (notification)"
                    }
                },
                "required": ["message"]
            }
        },
        {
            "name": "get_current_time",
            "description": "Get the current date and time. Use this whenever you need to know what time it is right now.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
                "required": []
            }
        }
    ]


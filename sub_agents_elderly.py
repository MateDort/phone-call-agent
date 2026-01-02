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
        """Edit a reminder - can update title, time, or both."""
        # Find reminder by title or time
        reminders = self.db.get_reminders(active_only=True)
        match = None
        
        # Try to find by title first
        title = args.get("title", "")
        old_title = args.get("old_title", "")
        old_time = args.get("old_time", "")
        
        search_title = old_title or title
        
        for r in reminders:
            # Match by title
            if search_title and search_title.lower() in r['title'].lower():
                match = r
                break
            
            # Match by time
            if old_time:
                reminder_time = datetime.fromisoformat(r['datetime'])
                time_str = reminder_time.strftime('%I:%M %p').lower()
                if old_time.lower() in time_str or old_time.lower() in reminder_time.strftime('%I %p').lower():
                    match = r
                    break
        
        if not match:
            search_term = search_title or old_time or "reminder"
            return f"{get_text('couldnt_find_reminder', Config.LANGUAGE)}: {search_term}"
        
        # Prepare updates
        updates = {}
        
        # Update title if provided
        new_title = args.get("new_title", "")
        if new_title:
            updates["title"] = new_title
        elif "title" in args and args["title"] and args["title"] != match['title']:
            updates["title"] = args["title"]
        
        # Update time if provided
        new_time = args.get("new_time", "")
        time_str = args.get("time", "")
        if new_time or time_str:
            time_to_parse = new_time or time_str
            parsed = self._parse_time(time_to_parse)
            if not parsed:
                return f"{get_text('time_parse_error', Config.LANGUAGE)} '{time_to_parse}'"
            
            updates["datetime"] = parsed['datetime'].isoformat()
            if parsed.get('recurrence'):
                updates["recurrence"] = parsed['recurrence']
            if parsed.get('days_of_week'):
                updates["days_of_week"] = parsed['days_of_week']
        
        if not updates:
            return "No changes specified for the reminder"
        
        # Update reminder
        self.db.update_reminder(match['id'], **updates)
        
        logger.info(f"Updated reminder {match['id']}: {updates}")
        
        # Get updated reminder for response
        updated = self.db.get_reminder(match['id'])
        if updated:
            reminder_time = datetime.fromisoformat(updated['datetime'])
            time_str = reminder_time.strftime('%I:%M %p on %B %d, %Y')
            
            recurrence_text = ""
            if updated['recurrence'] == 'daily':
                recurrence_text = f" {get_text('every_day', Config.LANGUAGE)}"
            elif updated['recurrence'] == 'weekly' and updated['days_of_week']:
                recurrence_text = f" {get_text('every', Config.LANGUAGE)} {updated['days_of_week']}"
            
            return f"{get_text('reminder_updated', Config.LANGUAGE)}: {updated['title']} {get_text('at', Config.LANGUAGE)} {time_str}{recurrence_text}"
        
        return f"{get_text('reminder_updated', Config.LANGUAGE)}"
    
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
                "action": "lookup|list|birthday_check|add|edit",
                "name": str,
                "relation": str (optional),
                "phone": str (optional),
                "birthday": str (optional, YYYY-MM-DD format),
                "notes": str (optional),
                "old_name": str (for edit - name to find),
                "new_name": str (for edit - new name)
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
        
        elif action == "add":
            return await self._add_contact(args)
        
        elif action == "edit":
            return await self._edit_contact(args)
        
        else:
            return f"{get_text('unknown_contact_action', Config.LANGUAGE)}: {action}"
    
    async def _add_contact(self, args: Dict[str, Any]) -> str:
        """Add a new contact."""
        name = args.get("name", "")
        if not name:
            return "Please provide a name for the contact"
        
        relation = args.get("relation")
        phone = args.get("phone")
        birthday = args.get("birthday")
        notes = args.get("notes")
        
        # Check if contact already exists
        existing = self.db.search_contact(name)
        if existing:
            return f"A contact named {name} already exists. Use edit to update it."
        
        # Add contact
        contact_id = self.db.add_contact(
            name=name,
            relation=relation,
            phone=phone,
            birthday=birthday,
            notes=notes
        )
        
        logger.info(f"Added contact {contact_id}: {name}")
        
        # Build response
        info = [f"{get_text('contact_added', Config.LANGUAGE)}: {name}"]
        if relation:
            info.append(f"{get_text('relation', Config.LANGUAGE)}: {relation}")
        if phone:
            info.append(f"{get_text('phone', Config.LANGUAGE)}: {phone}")
        if birthday:
            info.append(f"{get_text('birthday', Config.LANGUAGE)}: {self._format_birthday(birthday)}")
        
        return "\n".join(info)
    
    async def _edit_contact(self, args: Dict[str, Any]) -> str:
        """Edit an existing contact."""
        # Find contact by name (old_name or name)
        old_name = args.get("old_name") or args.get("name", "")
        if not old_name:
            return get_text('couldnt_find_contact', Config.LANGUAGE)
        
        contact = self.db.search_contact(old_name)
        if not contact:
            return f"{get_text('couldnt_find_contact', Config.LANGUAGE)}: {old_name}"
        
        # Prepare update fields
        updates = {}
        if "new_name" in args and args["new_name"]:
            updates["name"] = args["new_name"]
        elif "name" in args and args["name"] and args["name"] != old_name:
            updates["name"] = args["name"]
        
        if "relation" in args:
            updates["relation"] = args["relation"]
        if "phone" in args:
            updates["phone"] = args["phone"]
        if "birthday" in args:
            updates["birthday"] = args["birthday"]
        if "notes" in args:
            updates["notes"] = args["notes"]
        
        if not updates:
            return "No changes specified"
        
        # Update contact
        self.db.update_contact(contact['id'], **updates)
        
        logger.info(f"Updated contact {contact['id']}: {updates}")
        
        # Return updated contact info
        updated_contact = self.db.get_contacts()
        updated = next((c for c in updated_contact if c['id'] == contact['id']), None)
        
        if updated:
            info = [f"{get_text('contact_updated', Config.LANGUAGE)}: {updated['name']}"]
            if updated['relation']:
                info.append(f"{get_text('relation', Config.LANGUAGE)}: {updated['relation']}")
            if updated['phone']:
                info.append(f"{get_text('phone', Config.LANGUAGE)}: {updated['phone']}")
            if updated['birthday']:
                info.append(f"{get_text('birthday', Config.LANGUAGE)}: {self._format_birthday(updated['birthday'])}")
            return "\n".join(info)
        
        return f"{get_text('contact_updated', Config.LANGUAGE)}: {old_name}"
    
    def _format_birthday(self, birthday_str: str) -> str:
        """Format birthday string nicely."""
        try:
            bday = datetime.fromisoformat(birthday_str)
            return bday.strftime("%B %d, %Y")
        except:
            return birthday_str


class MessageAgent(SubAgent):
    """Agent for sending SMS and WhatsApp messages to the user."""
    
    def __init__(self, messaging_handler):
        super().__init__(
            name="message_agent",
            description="Sends SMS/WhatsApp messages and links to the user"
        )
        self.messaging_handler = messaging_handler
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Handle message sending request.
        
        Args:
            args: {
                "action": "send" or "send_link",
                "message": str (message text or link description),
                "link": str (URL for send_link action),
                "medium": "sms" or "whatsapp"
            }
        """
        action = args.get("action", "send")
        message = args.get("message", "")
        link = args.get("link", "")
        medium = args.get("medium", "sms")
        
        logger.info(f"MessageAgent: {action} via {medium}")
        
        if action == "send_link":
            # Send a link with optional description
            self.messaging_handler.send_link(
                to_number=Config.TARGET_PHONE_NUMBER,
                url=link,
                description=message,
                medium=medium
            )
            return f"Link sent via {medium}"
        else:
            # Send regular message
            self.messaging_handler.send_message(
                to_number=Config.TARGET_PHONE_NUMBER,
                message_body=message,
                medium=medium
            )
            return f"Message sent via {medium}"


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
def get_all_agents(db: Database, messaging_handler=None) -> Dict[str, SubAgent]:
    """Get all available sub-agents.
    
    Args:
        db: Database instance
        messaging_handler: Optional MessagingHandler instance for MessageAgent
    
    Returns:
        Dictionary of agent_name -> agent_instance
    """
    agents = {
        "reminder": ReminderAgent(db),
        "user_bio": UserBioAgent(db),
        "contacts": ContactsAgent(db),
        "notification": NotificationAgent(),
    }
    
    # Add message agent if messaging_handler is provided
    if messaging_handler:
        agents["message"] = MessageAgent(messaging_handler)
    
    return agents


def get_function_declarations() -> list:
    """Get function declarations for all sub-agents.
    
    Returns:
        List of function declarations for Gemini
    """
    return [
        {
            "name": "manage_reminder",
            "description": "Create, list, delete, or edit reminders. Supports recurring reminders (daily, weekly). Examples: 'remind me to take my pill every day at 3pm', 'what reminders do I have', 'delete my 8am reminder', 'change the 9am reminder to 10am', 'edit my pill reminder title to take medication', 'change my 3pm reminder time to 4pm'",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: create, list, delete, or edit"
                    },
                    "title": {
                        "type": "STRING",
                        "description": "Reminder description (e.g., 'take my pill'). For edit: can be used to find reminder or set new title"
                    },
                    "time": {
                        "type": "STRING",
                        "description": "When to remind: '3pm', 'tomorrow at 8am', 'every day at 1pm', 'every monday at 2pm'. For edit: new time for the reminder"
                    },
                    "old_title": {
                        "type": "STRING",
                        "description": "For edit: the current title/name of the reminder to find"
                    },
                    "old_time": {
                        "type": "STRING",
                        "description": "For edit: the current time of the reminder to find (e.g., '9am', '3pm')"
                    },
                    "new_title": {
                        "type": "STRING",
                        "description": "For edit: the new title/name for the reminder"
                    },
                    "new_time": {
                        "type": "STRING",
                        "description": "For edit: the new time for the reminder (e.g., '10am', 'tomorrow at 2pm')"
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
            "description": "Look up, add, edit, or manage family and friends contact information including phone numbers, birthdays, and relationships. Examples: 'what is Helen's phone number', 'add a new contact named Harry relationship friend phone number 555-1234', 'edit Harry's phone number to 555-5678', 'search for the hospital and save it as a contact'",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: lookup (find specific contact), list (all contacts), birthday_check (check today's birthdays), add (create new contact), or edit (update existing contact)"
                    },
                    "name": {
                        "type": "STRING",
                        "description": "Contact name. For lookup/add: the name. For edit: can be used to find contact or set new name"
                    },
                    "relation": {
                        "type": "STRING",
                        "description": "Relationship (e.g., 'friend', 'doctor', 'family'). For add/edit actions"
                    },
                    "phone": {
                        "type": "STRING",
                        "description": "Phone number. For add/edit actions"
                    },
                    "birthday": {
                        "type": "STRING",
                        "description": "Birthday in YYYY-MM-DD format (e.g., '2004-08-27'). For add/edit actions"
                    },
                    "notes": {
                        "type": "STRING",
                        "description": "Additional notes about the contact. For add/edit actions"
                    },
                    "old_name": {
                        "type": "STRING",
                        "description": "For edit: the current name of the contact to find"
                    },
                    "new_name": {
                        "type": "STRING",
                        "description": "For edit: the new name for the contact"
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
        },
        {
            "name": "send_message",
            "description": "Send a text message or link to the user via SMS or WhatsApp. Use this when user requests links during phone calls or to send follow-up information.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: 'send' (text message) or 'send_link' (send URL)"
                    },
                    "message": {
                        "type": "STRING",
                        "description": "Message text or link description"
                    },
                    "link": {
                        "type": "STRING",
                        "description": "URL to send (for send_link action)"
                    },
                    "medium": {
                        "type": "STRING",
                        "description": "Communication medium: 'sms' or 'whatsapp' (default: sms)"
                    }
                },
                "required": ["action", "message"]
            }
        }
    ]


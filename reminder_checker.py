"""Background service to check for due reminders and trigger phone calls."""
import asyncio
import logging
from datetime import datetime
from database import Database
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ReminderChecker:
    """Checks for due reminders and triggers notifications/calls."""
    
    def __init__(self, db: Database, call_trigger: Optional[Callable] = None):
        """Initialize reminder checker.
        
        Args:
            db: Database instance
            call_trigger: Async function to call when reminder is due
                         Should accept (reminder_dict) and make phone call
        """
        self.db = db
        self.call_trigger = call_trigger
        self.running = False
        self.in_phone_call = False
        self.check_interval = 60  # Check every 60 seconds
    
    async def start(self):
        """Start the background reminder checking loop."""
        self.running = True
        logger.info("Reminder checker started")
        
        while self.running:
            try:
                await self._check_reminders()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in reminder checker: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the reminder checker."""
        self.running = False
        logger.info("Reminder checker stopped")
    
    def set_in_call(self, in_call: bool):
        """Set whether user is currently in a phone call.
        
        Args:
            in_call: True if in call, False otherwise
        """
        self.in_phone_call = in_call
        logger.info(f"In-call status updated: {in_call}")
    
    async def _check_reminders(self):
        """Check for due reminders and handle them."""
        now = datetime.now()
        due_reminders = self.db.get_due_reminders(now)
        
        if not due_reminders:
            return
        
        logger.info(f"Found {len(due_reminders)} due reminder(s)")
        
        for reminder in due_reminders:
            await self._handle_due_reminder(reminder, now)
    
    async def _handle_due_reminder(self, reminder: dict, current_time: datetime):
        """Handle a due reminder.
        
        Args:
            reminder: Reminder dictionary
            current_time: Current datetime
        """
        reminder_id = reminder['id']
        title = reminder['title']
        
        logger.info(f"Processing due reminder: {title}")
        
        if self.in_phone_call:
            # User is already on the phone, announce it during the call
            logger.info(f"User in call - reminder will be announced: {title}")
            # The main agent will check for due reminders during the call
        else:
            # User not on call - trigger an outbound call
            logger.info(f"User not in call - triggering call for reminder: {title}")
            
            if self.call_trigger:
                try:
                    await self.call_trigger(reminder)
                except Exception as e:
                    logger.error(f"Error triggering call for reminder: {e}")
        
        # Mark as triggered
        self.db.mark_reminder_triggered(reminder_id)
        
        # If it's a recurring reminder, schedule next occurrence
        if reminder['recurrence']:
            await self._schedule_next_occurrence(reminder, current_time)
    
    async def _schedule_next_occurrence(self, reminder: dict, current_time: datetime):
        """Schedule next occurrence for recurring reminder.
        
        Args:
            reminder: Reminder dictionary
            current_time: Current datetime
        """
        reminder_time = datetime.fromisoformat(reminder['datetime'])
        next_time = None
        
        if reminder['recurrence'] == 'daily':
            # Schedule for same time tomorrow
            next_time = reminder_time.replace(
                year=current_time.year,
                month=current_time.month,
                day=current_time.day
            )
            # If that's in the past, move to tomorrow
            if next_time <= current_time:
                next_time = next_time.replace(day=next_time.day + 1)
        
        elif reminder['recurrence'] == 'weekly':
            # For weekly, the reminder will check days_of_week each day
            # Just move to tomorrow
            next_time = reminder_time.replace(day=reminder_time.day + 1)
        
        if next_time:
            self.db.update_reminder(
                reminder['id'],
                datetime=next_time.isoformat()
            )
            logger.info(f"Scheduled next occurrence for {reminder['title']} at {next_time}")
    
    def get_current_reminders_for_call(self) -> str:
        """Get formatted string of current due reminders for announcement.
        
        Returns:
            String describing due reminders
        """
        now = datetime.now()
        due_reminders = self.db.get_due_reminders(now)
        
        if not due_reminders:
            return None
        
        if len(due_reminders) == 1:
            return f"You have a reminder: {due_reminders[0]['title']}"
        else:
            titles = [r['title'] for r in due_reminders]
            return f"You have {len(due_reminders)} reminders: {', '.join(titles)}"


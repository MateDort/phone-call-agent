"""Sub-agents for specialized tasks."""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from gemini_live_client import SubAgent

logger = logging.getLogger(__name__)


class CalendarAgent(SubAgent):
    """Handles calendar and scheduling operations."""
    
    def __init__(self):
        super().__init__(
            name="calendar_agent",
            description="Manages calendar events and scheduling"
        )
        # Simple in-memory calendar (could be replaced with Google Calendar API)
        self.events = []
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Execute calendar operation.
        
        Args:
            args: {"action": "create|list|delete", "title": str, "date": str, ...}
        """
        action = args.get("action", "list")
        
        if action == "create":
            event = {
                "title": args.get("title", "Untitled"),
                "date": args.get("date", datetime.now().isoformat()),
                "description": args.get("description", "")
            }
            self.events.append(event)
            logger.info(f"Created event: {event['title']}")
            return f"Created calendar event: {event['title']} on {event['date']}"
        
        elif action == "list":
            if not self.events:
                return "No events scheduled"
            
            events_text = "\n".join([
                f"- {e['title']} on {e['date']}"
                for e in self.events
            ])
            return f"Upcoming events:\n{events_text}"
        
        elif action == "delete":
            title = args.get("title", "")
            self.events = [e for e in self.events if e['title'] != title]
            return f"Deleted event: {title}"
        
        else:
            return f"Unknown calendar action: {action}"


class DataLookupAgent(SubAgent):
    """Looks up information from a database or knowledge base."""
    
    def __init__(self):
        super().__init__(
            name="data_lookup",
            description="Searches internal knowledge base for information"
        )
        # Mock database
        self.knowledge_base = {
            "company_hours": "Monday-Friday 9AM-5PM EST",
            "support_email": "support@example.com",
            "return_policy": "30-day money back guarantee on all products",
            "shipping_time": "Standard shipping: 5-7 business days, Express: 2-3 business days",
        }
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Look up information.
        
        Args:
            args: {"query": str} - what to search for
        """
        query = args.get("query", "").lower()
        
        # Simple keyword matching
        results = []
        for key, value in self.knowledge_base.items():
            if any(word in key for word in query.split()):
                results.append(f"{key}: {value}")
        
        if results:
            return "\n".join(results)
        else:
            # Simulate database search
            return f"No information found for '{query}' in the knowledge base"


class CustomerServiceAgent(SubAgent):
    """Handles customer service operations."""
    
    def __init__(self):
        super().__init__(
            name="customer_service",
            description="Assists with customer service requests and order management"
        )
        # Mock customer database
        self.customers = {
            "+14049525557": {
                "name": "John Doe",
                "orders": ["ORDER-123", "ORDER-456"],
                "status": "active"
            }
        }
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Handle customer service request.
        
        Args:
            args: {"action": "lookup|order_status", "customer_id": str, "order_id": str}
        """
        action = args.get("action", "lookup")
        customer_id = args.get("customer_id", "")
        
        if action == "lookup":
            customer = self.customers.get(customer_id)
            if customer:
                return f"Customer: {customer['name']}, Status: {customer['status']}, Orders: {len(customer['orders'])}"
            else:
                return f"Customer {customer_id} not found"
        
        elif action == "order_status":
            order_id = args.get("order_id", "")
            # Mock order status
            return f"Order {order_id} is currently in transit, expected delivery in 2 days"
        
        else:
            return f"Unknown customer service action: {action}"


class NotificationAgent(SubAgent):
    """Sends notifications and reminders."""
    
    def __init__(self):
        super().__init__(
            name="notification",
            description="Sends notifications, reminders, and alerts"
        )
        self.scheduled_notifications = []
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Schedule or send notification.
        
        Args:
            args: {"message": str, "delay_seconds": int (optional)}
        """
        message = args.get("message", "")
        delay = args.get("delay_seconds", 0)
        
        if delay > 0:
            # Schedule for later
            notification = {
                "message": message,
                "scheduled_for": (datetime.now() + timedelta(seconds=delay)).isoformat()
            }
            self.scheduled_notifications.append(notification)
            logger.info(f"Scheduled notification: {message} in {delay} seconds")
            return f"Notification scheduled for {delay} seconds from now"
        else:
            # Immediate notification
            logger.info(f"Sending notification: {message}")
            return f"Notification sent: {message}"


class CalculatorAgent(SubAgent):
    """Performs calculations and conversions."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Performs mathematical calculations and unit conversions"
        )
    
    async def execute(self, args: Dict[str, Any]) -> str:
        """Perform calculation.
        
        Args:
            args: {"operation": str, "values": list}
        """
        operation = args.get("operation", "")
        values = args.get("values", [])
        
        try:
            if operation == "add":
                result = sum(float(v) for v in values)
                return f"Sum: {result}"
            
            elif operation == "multiply":
                result = 1
                for v in values:
                    result *= float(v)
                return f"Product: {result}"
            
            elif operation == "divide":
                if len(values) != 2:
                    return "Division requires exactly 2 values"
                result = float(values[0]) / float(values[1])
                return f"Result: {result}"
            
            else:
                return f"Unknown operation: {operation}"
                
        except Exception as e:
            return f"Calculation error: {e}"


# Agent registry - easy way to access all agents
def get_all_agents() -> Dict[str, SubAgent]:
    """Get all available sub-agents.
    
    Returns:
        Dictionary of agent_name -> agent_instance
    """
    return {
        "calendar": CalendarAgent(),
        "data_lookup": DataLookupAgent(),
        "customer_service": CustomerServiceAgent(),
        "notification": NotificationAgent(),
        "calculator": CalculatorAgent(),
    }


def get_function_declarations() -> list:
    """Get function declarations for all sub-agents.
    
    Returns:
        List of function declarations for Gemini
    """
    return [
        {
            "name": "manage_calendar",
            "description": "Create, list, or delete calendar events",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action to perform: create, list, or delete"
                    },
                    "title": {
                        "type": "STRING",
                        "description": "Event title (for create/delete)"
                    },
                    "date": {
                        "type": "STRING",
                        "description": "Event date in ISO format (for create)"
                    },
                    "description": {
                        "type": "STRING",
                        "description": "Event description (for create)"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "lookup_information",
            "description": "Search the internal knowledge base for company information, policies, hours, etc.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "What to search for"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "customer_service",
            "description": "Look up customer information or order status",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "description": "Action: lookup (customer info) or order_status"
                    },
                    "customer_id": {
                        "type": "STRING",
                        "description": "Customer phone number or ID"
                    },
                    "order_id": {
                        "type": "STRING",
                        "description": "Order ID (for order_status)"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "send_notification",
            "description": "Send a notification or reminder",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "message": {
                        "type": "STRING",
                        "description": "Notification message"
                    },
                    "delay_seconds": {
                        "type": "NUMBER",
                        "description": "Delay before sending (optional, default: 0)"
                    }
                },
                "required": ["message"]
            }
        },
        {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "description": "Operation: add, multiply, divide"
                    },
                    "values": {
                        "type": "ARRAY",
                        "description": "Numbers to calculate",
                        "items": {"type": "NUMBER"}
                    }
                },
                "required": ["operation", "values"]
            }
        }
    ]


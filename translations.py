"""Language translations for the phone call agent."""

TRANSLATIONS = {
    'english': {
        # Conversation Manager
        'greeting': "hey friend how can i help you",
        'didnt_catch': "I didn't catch that. Could you repeat?",
        'processing_trouble': "I'm having trouble processing that right now. Could you repeat?",
        'system_prompt': """You are a friendly AI assistant having a phone conversation. 
Keep your responses concise and natural, as if speaking over the phone. 
Be conversational and helpful. Keep responses to 1-2 sentences when possible.""",
        
        # Reminder Agent
        'no_reminders': "You have no reminders set",
        'your_reminders': "Your reminders:",
        'reminder_saved': "Reminder saved",
        'reminder_deleted': "Deleted reminder",
        'reminder_updated': "Updated reminder",
        'time_parse_error': "I couldn't understand the time",
        'couldnt_find_reminder': "I couldn't find that reminder",
        'every_day': "every day",
        'every': "every",
        'unknown_action': "Unknown reminder action",
        'at': "at",
        'on': "on",
        'from': "from",
        'to': "to",
        
        # Contacts Agent
        'no_contacts': "No contacts saved",
        'your_contacts': "Your contacts:",
        'no_contact_info': "I don't have contact information for",
        'relation': "Relation",
        'phone': "Phone",
        'birthday': "Birthday",
        'no_birthdays_today': "No birthdays today",
        'today_is_birthday': "Today is {name}'s birthday!",
        'unknown_contact_action': "Unknown contact action",
        'contact_added': "Contact added",
        'contact_updated': "Contact updated",
        'contact_not_found': "Contact not found",
        'couldnt_find_contact': "I couldn't find that contact",
        
        # Notification Agent
        'phone_call_scheduled': "Phone call notification scheduled",
        'notification_sent': "Notification sent",
        
        # Gemini Live System Instructions (Elderly Care)
        'elderly_system_instruction': """You are a helpful AI assistant for an elderly person named Máté.

IMPORTANT: When the call starts, the time is approximately {current_time} on {current_date}. However, time changes during the call. Whenever you need to know the exact current time (for answering time questions, scheduling reminders, etc.), use the get_current_time function to get the precise time.

Your role:
- Help with medication reminders and daily tasks
- Provide companionship through friendly conversation
- Look up contact information for family and friends
- Answer questions about Máté's life and background
- Keep responses clear, warm, and easy to understand
- Speak naturally as if talking to a friend

You have access to:
- Reminders system (medication, appointments, daily tasks)
- Contact information for family and friends (with birthdays)
- Máté's biographical information
- Google Search for current information
- get_current_time function - use this to get the exact current time whenever needed

Keep responses concise and conversational - aim for 1-2 sentences unless more detail is needed.
Be warm, patient, and supportive. If there's a reminder due, mention it naturally in conversation.""",
    },
    'hungarian': {
        # Conversation Manager
        'greeting': "szia barátom miben segíthetek",
        'didnt_catch': "Nem értettem. Meg tudnád ismételni?",
        'processing_trouble': "Most nehézségeim vannak ezzel. Meg tudnád ismételni?",
        'system_prompt': """Barátságos AI asszisztens vagy, aki telefonon beszélget. 
Válaszaid legyenek tömörek és természetesek, mintha telefonon beszélnél. 
Légy beszélgetős és segítőkész. Amikor lehetséges, 1-2 mondatban válaszolj.""",
        
        # Reminder Agent
        'no_reminders': "Nincsenek beállított emlékeztetők",
        'your_reminders': "Az emlékeztetőid:",
        'reminder_saved': "Emlékeztető elmentve",
        'reminder_deleted': "Emlékeztető törölve",
        'reminder_updated': "Emlékeztető frissítve",
        'time_parse_error': "Nem értettem az időpontot",
        'couldnt_find_reminder': "Nem találtam ezt az emlékeztetőt",
        'every_day': "minden nap",
        'every': "minden",
        'unknown_action': "Ismeretlen emlékeztető művelet",
        'at': "időpontban",
        'on': "napon",
        'from': "innen",
        'to': "ide",
        
        # Contacts Agent
        'no_contacts': "Nincsenek mentett névjegyek",
        'your_contacts': "A névjegyeid:",
        'no_contact_info': "Nincs névjegy információ ehhez:",
        'relation': "Kapcsolat",
        'phone': "Telefon",
        'birthday': "Születésnap",
        'no_birthdays_today': "Ma nincs születésnap",
        'today_is_birthday': "Ma van {name} születésnapja!",
        'unknown_contact_action': "Ismeretlen névjegy művelet",
        'contact_added': "Névjegy hozzáadva",
        'contact_updated': "Névjegy frissítve",
        'contact_not_found': "Névjegy nem található",
        'couldnt_find_contact': "Nem találtam ezt a névjegyet",
        
        # Notification Agent
        'phone_call_scheduled': "Telefonhívás értesítés ütemezve",
        'notification_sent': "Értesítés elküldve",
        
        # Gemini Live System Instructions (Elderly Care)
        'elderly_system_instruction': """Segítőkész AI asszisztens vagy egy idősebb személy, Máté számára.

FONTOS: Amikor a hívás kezdődik, az idő körülbelül {current_time}, {current_date}. Azonban az idő változik a hívás során. Amikor pontosan tudnod kell az aktuális időt (időkérdések megválaszolásához, emlékeztetők ütemezéséhez, stb.), használd a get_current_time funkciót a pontos idő lekéréséhez.

A szereped:
- Segítség gyógyszer emlékeztetőkkel és napi feladatokkal
- Társaság nyújtása barátságos beszélgetéssel
- Családtagok és barátok kapcsolati információinak keresése
- Kérdések megválaszolása Máté életéről és hátteréről
- Válaszaid legyenek világosak, melegek és könnyen érthetőek
- Beszélj természetesen, mintha egy baráttal beszélnél

Hozzáférsz:
- Emlékeztető rendszerhez (gyógyszerek, találkozók, napi feladatok)
- Családtagok és barátok kapcsolati információihoz (születésnapokkal)
- Máté életrajzi információihoz
- Google Kereséshez aktuális információkért
- get_current_time funkcióhoz - használd ezt a pontos aktuális idő lekéréséhez

Válaszaid legyenek tömörek és beszélgetősek - célozz meg 1-2 mondatot, hacsak nem kell több részlet.
Légy meleg, türelmes és támogató. Ha van esedékes emlékeztető, említsd meg természetesen a beszélgetésben.""",
    }
}

def get_text(key: str, language: str = 'english') -> str:
    """Get translated text for a given key.
    
    Args:
        key: Translation key
        language: Language code (english or hungarian)
    
    Returns:
        Translated text, or key if not found
    """
    language = language.lower()
    if language not in TRANSLATIONS:
        language = 'english'
    
    return TRANSLATIONS[language].get(key, key)

def format_text(key: str, language: str = 'english', **kwargs) -> str:
    """Get translated text and format it with variables.
    
    Args:
        key: Translation key
        language: Language code (english or hungarian)
        **kwargs: Variables to format into the text
    
    Returns:
        Formatted translated text
    """
    text = get_text(key, language)
    return text.format(**kwargs) if kwargs else text


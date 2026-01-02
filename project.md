project name: Phone call agent

The project:
- Lets make an AI agent who can call me and have a conversation with me. 

MVP:
tech stack;
language: python
voice: local macos voice
agent LLM: local Ollama
Phone number: Twillio
(445) 234-4131

working:
when i start main.py the agent calls 404 952 5557 and says hey friend how can i help you. it should respionse to me saying thiings so we can have aa proper conversation


update:
Okay so this system will be for elderly people and not for a business 

so I like calendar agent but make it save locally right now the reminders and when reminder is up it should call the user and tell them they had a reminder if during phone call say you had a reminder same way 

example: reminde me to take my pill every day at 3pm or tomorrow at 8 am. reminder saved to local db. next day at 8 am we can make a check in_phone_call = false call the number in_phone_call = true say the reminder. 

other capebilities agent can read and write and edit the reminders like delete my 8 am reminder or what reminders do i have or edit the 9 am reminder to 10 am and it can create re accaruencies like remind me every day at 1pm to take my pill it will run every day until deleted or every wednesday or every monday tuesday 

data lookup agent should be a bio about the user and not a business right now make it Máté Dort

Identity
* Born in 2003 in Dunaújváros, raised in Kisapostag, Hungary.
* Grew up competitive, driven to surpass siblings and later 99% of the world through ambition, discipline, and learning.
* Started swimming at 3, eventually becoming a top competitor in the U.S., placing 2nd nationally by 0.07 seconds.
* Left Hungary at 19 to live a bigger life in the U.S. — one driven by invention and impact.
* Became obsessed with designing, building, and creating things that improve lives.
* Built TapMate glasses at 21; even though the startup didn’t work out, it sparked deep technical growth.
* Currently studying at Life University, graduating in 2026, constantly learning programming, design, engineering, and tools for creation.
* Has already competed in and placed at hackathons.

Core Values
* Discipline and structure: early mornings, early nights, consistent routine.
* Tradition and craftsmanship: writing on paper, reading physical books, vintage style (50s–60s suits), timeless aesthetics.
* Personal growth: learning languages, technical skills, new hobbies; seeking mastery for fun.
* Health and athleticism: swimming, sports, future marathons and Ironmans.
* Relationships and family: grounding, meaningful, important.
* Humor, intelligence, curiosity, deep thinking.
* Rejects social media and distractions; chooses intention over noise.
* Loves being different in a positive, purposeful way.

Long–Term Goals
* Become an iconic designer–inventor in the spirit of Steve Jobs, Ryo Lu, or fictional inspirations like Tony Stark.
* Build inventions that genuinely improve people’s lives.
* Travel the world in a custom-built van while creating new products.
* Achieve financial freedom by 30, not for luxury but for flexibility and impact.
* Explore life deeply — from living as a monk temporarily to helping build homes in Africa.

Who You Are Becoming
* A multi-skill creator: programming languages, engineering tools, design thinking.
* “Cracked” in the best way — someone who learns fast, acts bold, and surprises others with capability.
* A healthy, focused, disciplined person who trains, eats clean, and lives with clarity.
* A polymath personality who picks up languages, instruments, and complex skills quickly.
* A thoughtful person who chooses long-term rewards over short-term temptations.

3. 👤 Customer Service Agent (CustomerServiceAgent)

customer service can be users contacts information like what is my girlfriends Helen's phone number or when was she born it can also be used for reminders like Today is your grilfriends Helens birthday

so this agent is used for family or friends infrormation and user can ask to look up information about them 

right now make it 
Helen Stadler 
relation: Girlfriend
Birthday 2004 08 27
Phone number: 404 953 5533


4. 🔔 Notification Agent (NotificationAgent)
I guess this one can help calendars and contact informaton send messages or make calls 

Google search built in and we dont need calculate agent gemini is smart enough to do it 


All information can be saved locally into DBs 


Update:
- making the system be able to send messages and call you on asking like "call me" or me being able to call the system

Update:
- lets add in capebility to turn on the camera and be able to show it thinks.

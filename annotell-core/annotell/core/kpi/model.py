from dataclasses import dataclass

@dataclass
class Event:
    session_id: int
    event_type: str
    event_context: str
    event_time: int

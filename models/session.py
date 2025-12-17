# session.py
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

class SessionState:
    """
    Holds per-user session state:
    - Message history
    - Last-known behavioral signals (e.g., formality)
    - Attached automata for scoring/state transitions
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.automata = None  # Attached externally (SessionAutomata)
        self.messages: list[dict] = []

    # -------------------------
    # Message storage
    # -------------------------
    def add_message(
        self,
        message_text: str,
        formality: int = 0,
        off_platform: bool = False,
        sent_time: Optional[datetime] = None,
    ):
        """
        Persist a processed message with metadata.
        Ensures timestamps are timezone-aware (Asia/Manila).
        """
        tz = ZoneInfo("Asia/Manila")

        if sent_time is None:
            sent_time = datetime.now(tz)
        elif sent_time.tzinfo is None:
            sent_time = sent_time.replace(tzinfo=tz)

        self.messages.append({
            "text": message_text,
            "timestamp": sent_time,
            "previous_formality": self.get_last_formality(),
            "current_formality": formality,
            "off_platform": off_platform,
        })

    # -------------------------
    # Lightweight session metrics
    # -------------------------
    def get_last_formality(self) -> int:
        """Return last message's formality score, or 0 if none."""
        if not self.messages:
            return 0
        return self.messages[-1]["current_formality"]

    def message_index(self) -> int:
        """1-based message index for this session."""
        return len(self.messages)

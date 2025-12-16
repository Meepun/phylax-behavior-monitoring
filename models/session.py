# session.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class SessionState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.automata = None  # Attach automata externally
        self.messages = []

    # -------------------------
    # Message storage
    # -------------------------
    def add_message(self, message_text, formality=0, off_platform=False, sent_time=None):
        # Ensure sent_time is timezone-aware (default Manila)
        if sent_time is None:
            sent_time = datetime.now(ZoneInfo("Asia/Manila"))
        elif sent_time.tzinfo is None:
            sent_time = sent_time.replace(tzinfo=ZoneInfo("Asia/Manila"))

        msg_data = {
            "text": message_text,
            "timestamp": sent_time,
            "previous_formality": self.get_last_formality(),
            "current_formality": formality,
            "off_platform": off_platform
        }
        self.messages.append(msg_data)

    # -------------------------
    # Metrics for Analyzer/Prolog
    # -------------------------
    def get_last_formality(self):
        if not self.messages:
            return 0
        return self.messages[-1]["current_formality"]

    def prev_5min_count(self, now=None):
        """Messages in the last 5 minutes excluding the current one"""
        if not self.messages:
            return 0
        now = now or datetime.now(ZoneInfo("Asia/Manila"))
        five_min_ago = now - timedelta(minutes=5)
        return sum(
            1 for m in self.messages[:-1]
            if five_min_ago <= m["timestamp"] < now
        )

    def curr_5min_count(self, now=None):
        """Messages in the last 5 minutes including the current one"""
        if not self.messages:
            return 0
        now = now or datetime.now(ZoneInfo("Asia/Manila"))
        five_min_ago = now - timedelta(minutes=5)
        return sum(
            1 for m in self.messages
            if m["timestamp"] >= five_min_ago
        )

    def message_index(self):
        return len(self.messages)

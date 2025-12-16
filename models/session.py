# logic for managing user session states
from datetime import datetime, timedelta

class SessionState:
    def __init__(self, user_id):
        self.user_id = user_id

        # Weighted suspicion score
        self.score = 0

        # Automata-related state
        self.state = "NORMAL"

        # Context for analysis
        self.previous_style = None
        self.last_message_time = None

        # Dual-condition decay tracking
        self.clean_message_count = 0
        self.clean_window_start = None

        # Store message history with metadata
        self.messages = []  # each message: {"text", "timestamp", "previous_formality", "current_formality", "off_platform"}

    # -------------------------
    # Session Updates
    # -------------------------
    def add_message(self, message_text, formality=0, off_platform=False, sent_time=None):
        sent_time = sent_time or datetime.utcnow()
        msg_data = {
            "text": message_text,
            "timestamp": sent_time,
            "previous_formality": self.get_last_formality(),
            "current_formality": formality,
            "off_platform": off_platform
        }
        self.messages.append(msg_data)
        self.last_message_time = sent_time

    def add_violation(self, weight):
        self.score += weight
        # Reset decay tracking
        self.clean_message_count = 0
        self.clean_window_start = None
        self._update_state()

    def add_clean_message(self):
        now = datetime.utcnow()

        if self.clean_window_start is None:
            self.clean_window_start = now
            self.clean_message_count = 1
        else:
            self.clean_message_count += 1

        if self._can_decay(now):
            self.score = max(0, self.score - 1)
            self.clean_message_count = 0
            self.clean_window_start = None

        self._update_state()

    # -------------------------
    # Metrics for Prolog
    # -------------------------
    def get_last_formality(self):
        if not self.messages:
            return 0
        return self.messages[-1]["current_formality"]

    def prev_5min_count(self):
        """Messages in last 5 minutes excluding current"""
        if not self.messages:
            return 0
        now = datetime.utcnow()
        five_min_ago = now - timedelta(minutes=5)
        return sum(1 for m in self.messages[:-1] if five_min_ago <= m["timestamp"] < now)

    def curr_5min_count(self):
        """Messages in last 5 minutes including current"""
        if not self.messages:
            return 0
        now = datetime.utcnow()
        five_min_ago = now - timedelta(minutes=5)
        return sum(1 for m in self.messages if m["timestamp"] >= five_min_ago)

    def message_index(self):
        return len(self.messages)

    # -------------------------
    # Decay logic
    # -------------------------
    def _can_decay(self, now):
        return (
            self.clean_message_count >= 5 and
            now - self.clean_window_start <= timedelta(minutes=10)
        )

    # -------------------------
    # Automata state updates
    # -------------------------
    def _update_state(self):
        if self.score >= 10:
            self.state = "LOCKED"
        elif self.score >= 7:
            self.state = "FLAGGED_TWICE"
        elif self.score >= 4:
            self.state = "FLAGGED_ONCE"
        else:
            self.state = "NORMAL"

    def is_locked(self):
        return self.state == "LOCKED"

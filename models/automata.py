# automata.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class SessionAutomata:
    """
    Handles session state transitions and score decay based on messages.
    """

    DECAY_COUNT = 5            # Number of clean messages needed for decay
    DECAY_WINDOW_MINUTES = 10  # Time window in minutes to count clean messages for decay
    TZ = ZoneInfo("Asia/Manila")  # default timezone for decay calculations

    def __init__(self):
        self.score = 0
        self.state = "NORMAL"
        self.clean_message_count = 0
        self.clean_window_start = None

    # -------------------------
    # Violation Handling
    # -------------------------
    def add_violation(self, weight: int):
        """Increase score due to a violation and reset decay tracking."""
        self.score += weight
        self._reset_decay()
        self._update_state()

    # -------------------------
    # Decay Handling
    # -------------------------
    def add_clean_message(self, message_time: datetime = None):
        """
        Process a clean message, possibly triggering score decay.
        message_time: aware datetime in the TZ zone
        """
        now = message_time or datetime.now(self.TZ)

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

    def _can_decay(self, now: datetime) -> bool:
        """Check if decay conditions are met."""
        return (
            self.clean_message_count >= self.DECAY_COUNT and
            now - self.clean_window_start <= timedelta(minutes=self.DECAY_WINDOW_MINUTES)
        )

    def _reset_decay(self):
        """Reset decay tracking after a violation."""
        self.clean_message_count = 0
        self.clean_window_start = None

    # -------------------------
    # State Updates
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

    def is_locked(self) -> bool:
        return self.state == "LOCKED"

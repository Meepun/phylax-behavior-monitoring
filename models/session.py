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

    # Add a violation with its weight
    def add_violation(self, weight):
        self.score += weight
        # Reset decay tracking
        self.clean_message_count = 0
        self.clean_window_start = None
        self._update_state()

    # Register a clean (non-violating) message
    def add_clean_message(self):
        now = datetime.utcnow()

        if self.clean_window_start is None:
            self.clean_window_start = now
            self.clean_message_count = 1
            return

        self.clean_message_count += 1

        if self._can_decay(now):
            self.score = max(0, self.score - 1)
            self.clean_message_count = 0
            self.clean_window_start = None

        self._update_state()

    # Check if decay conditions are met
    def _can_decay(self, now):
        # Example: at least 5 clean messages within 10 minutes
        return (
            self.clean_message_count >= 5 and
            now - self.clean_window_start <= timedelta(minutes=10)
        )

    # Update session state based on score
    def _update_state(self):
        if self.score >= 10:
            self.state = "LOCKED"
        elif self.score >= 7:
            self.state = "FLAGGED_TWICE"
        elif self.score >= 4:
            self.state = "FLAGGED_ONCE"
        else:
            self.state = "NORMAL"

    # Convenience method
    def is_locked(self):
        return self.state == "LOCKED"

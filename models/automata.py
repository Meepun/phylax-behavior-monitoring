# automata.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class SessionAutomata:
    DECAY_COUNT = 5            # Clean messages needed
    DECAY_WINDOW_MINUTES = 1  # Minutes to wait after being flagged. Set to 1min for demo
    TZ = ZoneInfo("Asia/Manila")

    STATE_THRESHOLDS = {
        "NORMAL": 0,
        "FLAGGED_ONCE": 4,
        "FLAGGED_TWICE": 7,
        "LOCKED": 10
    }

    def __init__(self):
        self.score = 0
        self.state = "NORMAL"
        self.clean_message_count = 0
        self.last_flag_time = None  # Timestamp of last violation that caused flag

    # -------------------------
    # Violation Handling
    # -------------------------
    def add_violation(self, weight: int, message_time: datetime = None):
        """Increase score due to a violation and reset decay tracking."""
        self.score += weight
        self._reset_decay()
        self.last_flag_time = message_time or datetime.now(self.TZ)  # set flag time for decay
        self._update_state()


    # -------------------------
    # Decay Handling
    # -------------------------
    def add_clean_message(self, message_time: datetime = None):
        now = message_time or datetime.now(self.TZ)
        self.clean_message_count += 1

        if self.state in ["FLAGGED_ONCE", "FLAGGED_TWICE"]:
            if self.last_flag_time:
                elapsed = now - self.last_flag_time
                if (elapsed >= timedelta(minutes=self.DECAY_WINDOW_MINUTES) and
                    self.clean_message_count >= self.DECAY_COUNT):

                    # Reduce to previous state's minimum threshold
                    if self.state == "FLAGGED_TWICE":
                        self.score = self.STATE_THRESHOLDS["FLAGGED_ONCE"]
                    elif self.state == "FLAGGED_ONCE":
                        self.score = self.STATE_THRESHOLDS["NORMAL"]

                    self.clean_message_count = 0
                    self.last_flag_time = now  # reset timer to now for next decay

        self._update_state()

    # -------------------------
    # Reset decay counter after a violation
    # -------------------------
    def _reset_decay(self):
        self.clean_message_count = 0

    # -------------------------
    # State Updates
    # -------------------------
    def _update_state(self):
        if self.score >= self.STATE_THRESHOLDS["LOCKED"]:
            self.state = "LOCKED"
        elif self.score >= self.STATE_THRESHOLDS["FLAGGED_TWICE"]:
            self.state = "FLAGGED_TWICE"
        elif self.score >= self.STATE_THRESHOLDS["FLAGGED_ONCE"]:
            self.state = "FLAGGED_ONCE"
        else:
            self.state = "NORMAL"

    def is_locked(self) -> bool:
        return self.state == "LOCKED"

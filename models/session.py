# logic for managing user session states
class SessionState:
    def __init__(self, user_id):
        self.user_id = user_id

        # Automata-related state
        self.flag_count = 0
        self.state = "NORMAL"

        # Context for future analysis
        self.previous_style = None
        self.last_message_time = None

    def register_flag(self):
        self.flag_count += 1

        if self.flag_count == 1:
            self.state = "FLAGGED_ONCE"
        elif self.flag_count == 2:
            self.state = "FLAGGED_TWICE"
        elif self.flag_count >= 3:
            self.state = "LOCKED"

    def is_locked(self):
        return self.state == "LOCKED"

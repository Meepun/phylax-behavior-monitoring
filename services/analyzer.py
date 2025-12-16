# analyzer.py
from datetime import datetime, timezone

OFF_PLATFORM_KEYWORDS = [
    "telegram", "whatsapp", "viber",
    "call me", "text me", "email me",
    "pm me", "dm me"
]

# -----------------------------
# Formality signals
# -----------------------------
FORMAL_PHRASES = [
    "could you", "may i", "kindly",
    "please be advised", "we would like to",
    "for your reference", "we regret to inform you"
]

FORMAL_TITLES = [
    "mr.", "ms.", "mrs.", "sir", "ma'am", "dr.", "prof."
]

NO_CONTRACTION_PHRASES = [
    "i am", "it is", "we are", "you are"
]

CASUAL_MARKERS = [
    "lol", "lmao", "bro", "dude", "hey", "yo",
    "gonna", "wanna", "lemme", "sup", "nah"
]

CONTRACTIONS = [
    "i'm", "it's", "we're", "you're", "can't", "won't", "don't"
]


class MessageAnalyzer:
    """
    Processes messages and prepares context for Prolog analysis.
    Computes behavioral metrics such as formality, off-platform requests,
    and message frequency. Assigns explicit formality levels for Prolog rules.
    """

    def __init__(self, session):
        self.session = session

    # -----------------------------
    # Core context computation
    # -----------------------------
    def compute_context(self, message_text, sent_hour=None, sent_time=None):
        now = sent_time or datetime.now(timezone.utc)
        sent_hour = sent_hour if sent_hour is not None else now.hour

        prev_5min = self.session.prev_5min_count(now)
        curr_5min = self.session.curr_5min_count(now)
        last_formality = self.session.get_last_formality()

        off_platform_request = any(
            k in message_text.lower() for k in OFF_PLATFORM_KEYWORDS
        )

        current_formality = self._score_formality(message_text)

        context = {
            "message": message_text,
            "message_index": self.session.message_index() + 1,
            "sent_hour": sent_hour,
            "prev_5min_count": prev_5min,
            "curr_5min_count": curr_5min,
            "previous_formality": last_formality,
            "current_formality": current_formality,
            "off_platform_request": off_platform_request
        }

        return context

    # -----------------------------
    # Formality scoring logic
    # -----------------------------
    def _score_formality(self, text: str) -> int:
        """
        Returns a discrete formality score for Prolog:
        0-1: Very casual
        2: Neutral
        3-4: Very formal
        """
        text_l = text.lower()
        score = 2  # neutral baseline

        # Increase formality
        if any(p in text_l for p in FORMAL_PHRASES):
            score += 1
        if any(t in text_l for t in FORMAL_TITLES):
            score += 1
        if any(nc in text_l for nc in NO_CONTRACTION_PHRASES):
            score += 1

        # Decrease formality
        if any(c in text_l for c in CASUAL_MARKERS):
            score -= 1
        if any(con in text_l for con in CONTRACTIONS):
            score -= 1

        # Clamp between 0 and 4
        score = max(0, min(4, score))

        # Explicitly classify for Prolog rules
        if score <= 1:
            return 0  # very casual
        elif score >= 3:
            return 4  # very formal
        else:
            return 2  # neutral

    # -----------------------------
    # Static helper for routes.py
    # -----------------------------
    @staticmethod
    def build_context(message_text, session, sent_time=None, sent_hour=None):
        analyzer = MessageAnalyzer(session)
        return analyzer.compute_context(
            message_text,
            sent_time=sent_time,
            sent_hour=sent_hour
        )

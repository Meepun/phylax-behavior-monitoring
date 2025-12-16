from pyswip import Prolog
import uuid
import os


class PrologEngine:
    def __init__(self):
        self.prolog = Prolog()
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        kb_path = os.path.join(
            os.path.dirname(__file__),
            "behavior_kb.pl"
        )
        self.prolog.consult(kb_path)

    # ----------------------------
    # PUBLIC API
    # ----------------------------
    def analyze_message(self, context: dict):
        msg_id = f"msg_{uuid.uuid4().hex}"

        self.assert_message_facts(msg_id, context)
        violations = self.query_violations(msg_id)
        self._cleanup_facts(msg_id)

        return violations

    # ----------------------------
    # INTERNALS
    # ----------------------------
    def assert_message_facts(self, msg_id, ctx):
        """Assert all necessary facts for a message (case-insensitive)."""
        def assertz(fact):
            self.prolog.assertz(fact)

        # Normalize message text (lowercase + escape quotes)
        normalized_message = ctx["message"].lower().replace('"', '\\"')
        assertz(f'message({msg_id}, "{normalized_message}")')

        # Behavioral facts
        assertz(f'prev_5min_count({msg_id}, {ctx.get("prev_5min_count", 0)})')
        assertz(f'curr_5min_count({msg_id}, {ctx.get("curr_5min_count", 0)})')
        if "previous_formality" in ctx:
            assertz(f'previous_formality({msg_id}, {ctx["previous_formality"]})')
        if "current_formality" in ctx:
            assertz(f'current_formality({msg_id}, {ctx["current_formality"]})')

        # Temporal facts
        if "sent_hour" in ctx:
            assertz(f'sent_hour({msg_id}, {ctx["sent_hour"]})')

        # Interaction facts
        if "message_index" in ctx:
            assertz(f'message_index({msg_id}, {ctx["message_index"]})')
        if ctx.get("off_platform_request"):
            # Use the renamed dynamic fact in behavior_kb.pl
            assertz(f'off_platform_request_fact({msg_id})')

    def query_violations(self, msg_id):
        """Query Prolog for all violations for this message."""
        results = self.prolog.query(f"behavioral_violation({msg_id}, V)")
        behavioral = [r["V"] for r in results]

        results = self.prolog.query(f"temporal_violation({msg_id}, V)")
        temporal = [r["V"] for r in results]

        results = self.prolog.query(f"interaction_violation({msg_id}, V)")
        interaction = [r["V"] for r in results]

        results = self.prolog.query(f"linguistic_violation({msg_id}, V)")
        linguistic = [r["V"] for r in results]

        # Combine all violations and remove duplicates
        return list(set(behavioral + temporal + interaction + linguistic))

    def _cleanup_facts(self, msg_id):
        predicates = [
            "message",
            "prev_5min_count",
            "curr_5min_count",
            "previous_formality",
            "current_formality",
            "sent_hour",
            "message_index",
            "off_platform_request_fact"
        ]

        for p in predicates:
            # Retract all facts for this msg_id (handles 1-arg and 2-arg predicates)
            list(self.prolog.query(f"retractall({p}({msg_id}, _))"))
            list(self.prolog.query(f"retractall({p}({msg_id}))"))


if __name__ == "__main__":
    engine = PrologEngine()

    violations = engine.analyze_message({
        "message": "From the bank po kami, please message me on Telegram",
        "prev_5min_count": 2,
        "curr_5min_count": 6,
        "previous_formality": 0,
        "current_formality": 2,
        "sent_hour": 2,
        "message_index": 1,
        "off_platform_request": True
    })

    print(violations)

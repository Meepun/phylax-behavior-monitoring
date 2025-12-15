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

        self._assert_facts(msg_id, context)
        violations = self._query_violations(msg_id)
        self._cleanup_facts(msg_id)

        return violations

    # ----------------------------
    # INTERNALS
    # ----------------------------
    def _assert_facts(self, msg_id, ctx):
        def assertz(fact):
            self.prolog.assertz(fact)

        # Message
        assertz(f'message({msg_id}, "{ctx["message"].lower()}")')

        # Behavioral
        assertz(f'message_count_last_minute({msg_id}, {ctx.get("message_count_last_minute", 1)})')
        assertz(f'average_message_count({msg_id}, {ctx.get("average_message_count", 1)})')

        # Style
        if ctx.get("previous_style"):
            assertz(f'previous_style({msg_id}, {ctx["previous_style"]})')
        if ctx.get("current_style"):
            assertz(f'current_style({msg_id}, {ctx["current_style"]})')

        # Temporal
        if ctx.get("sent_hour") is not None:
            assertz(f'sent_hour({msg_id}, {ctx["sent_hour"]})')

        # Interaction
        if ctx.get("asked_off_platform"):
            assertz(f'asked_off_platform({msg_id})')

        if ctx.get("ignored_previous_reply"):
            assertz(f'ignored_previous_reply({msg_id})')

    def _query_violations(self, msg_id):
        results = self.prolog.query(f"violation({msg_id}, V)")
        return list({r["V"] for r in results})

    def _cleanup_facts(self, msg_id):
        predicates = [
            "message",
            "message_count_last_minute",
            "average_message_count",
            "previous_style",
            "current_style",
            "sent_hour",
            "asked_off_platform",
            "ignored_previous_reply"
        ]

        for p in predicates:
            list(self.prolog.query(f"retractall({p}({msg_id}, _))"))
            list(self.prolog.query(f"retractall({p}({msg_id}))"))

if __name__ == "__main__":
    engine = PrologEngine()

    violations = engine.analyze_message({
        "message": "From the bank po kami, please message me on Telegram",
        "message_count_last_minute": 6,
        "average_message_count": 2,
        "previous_style": "casual",
        "current_style": "formal",
        "sent_hour": 2,
        "asked_off_platform": True,
        "ignored_previous_reply": True
    })

    print(violations)

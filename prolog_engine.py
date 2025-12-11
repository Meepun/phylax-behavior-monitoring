from pyswip import Prolog

prolog = Prolog()

# Define rule-based reasoning
prolog.assertz("suspicious(A) :- member(login_admin, A)")
prolog.assertz("suspicious(A) :- member(delete_logs, A)")
prolog.assertz("malicious(A) :- member(exfiltrate_data, A)")
prolog.assertz("malicious(A) :- member(disable_security, A)")

actions = []

def add_action(action):
    actions.append(action)

def classify_behavior():
    query_list = "[" + ",".join(actions) + "]"

    if list(prolog.query(f"suspicious({query_list})")):
        return "suspicious"

    if list(prolog.query(f"malicious({query_list})")):
        return "malicious"

    return "normal"


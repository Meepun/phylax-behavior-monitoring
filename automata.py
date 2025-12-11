automaton = {
    "states": ["S0", "S1", "S2", "BLOCKED"],
    "current_state": "S0",
    "transitions": {
        ("S0", "login"): "S1",
        ("S1", "open_file"): "S2",
        ("S2", "login_admin"): "BLOCKED"
    }
}

def apply_action(action):
    key = (automaton["current_state"], action)
    if key in automaton["transitions"]:
        automaton["current_state"] = automaton["transitions"][key]
    return automaton["current_state"]

def get_automaton_json():
    return {
        "states": automaton["states"],
        "current": automaton["current_state"],
        "transitions": [
            {"from": k[0], "to": v, "label": k[1]}
            for k, v in automaton["transitions"].items()
        ]
    }


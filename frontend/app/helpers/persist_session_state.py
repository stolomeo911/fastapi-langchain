import json
import os


def save_session_state(session_state, file_path="session_state.json"):
    # Filter out non-serializable items
    serializable_state = {key: value for key, value in session_state.items() if isinstance(value, (str, int, float, list, dict))}
    with open(file_path, "w") as f:
        json.dump(serializable_state, f)


def load_session_state(current_session_state, file_path="session_state.json"):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            session_state = json.load(f)
            current_session_state.update(session_state)

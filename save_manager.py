import json
from pathlib import Path

SAVE_FILE = Path(__file__).with_name("save.json")


def save_game(data):

    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        return True

    except (OSError, TypeError, ValueError) as error:
        print(f"Save error: {error}")
        return False


def load_game():

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return None

        required = ["story", "player", "current_room"]

        if not all(key in data for key in required):
            return None

        return data

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
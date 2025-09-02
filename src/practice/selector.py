import json
import random
from pathlib import Path

EXERCISE_FILE = Path(__file__).with_name('exercises.json')


def load_exercises():
    with open(EXERCISE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def pick_next(completed: dict) -> dict:
    """Pick next exercise based on difficulty.
    completed: {id: success(bool)}
    """
    exercises = load_exercises()
    # Simple strategy: pick random exercise not yet completed
    remaining = [ex for ex in exercises if ex['id'] not in completed]
    if not remaining:
        return {}
    # Sort by difficulty ascending for simplicity
    remaining.sort(key=lambda e: e['difficulty'])
    return random.choice(remaining[:2])

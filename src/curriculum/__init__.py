import json
from pathlib import Path

LESSON_FILE = Path(__file__).with_name("lessons.json")

def get_lessons():
    with open(LESSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

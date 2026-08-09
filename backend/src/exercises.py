"""
Hand-built reading exercise dataset for Learning & Literacy track.
Organised by level (beginner / intermediate / advanced) and topic.
Data source: hand-built local dataset (no public API exists for this specific need).
See README.md for data source notes.
"""

EXERCISES: dict[str, dict[str, list[dict]]] = {
    "beginner": {
        "animals": [
            {"word": "Cat", "sentence": "The cat sat on the mat.", "hint": "C - A - T"},
            {"word": "Dog", "sentence": "The dog is big.", "hint": "D - O - G"},
            {"word": "Cow", "sentence": "The cow gives milk.", "hint": "C - O - W"},
            {"word": "Hen", "sentence": "The hen lays eggs.", "hint": "H - E - N"},
            {"word": "Pig", "sentence": "The pig is pink.", "hint": "P - I - G"},
        ],
        "fruits": [
            {"word": "Mango", "sentence": "I like mango.", "hint": "M - A - N - G - O"},
            {"word": "Apple", "sentence": "The apple is red.", "hint": "A - P - P - L - E"},
            {"word": "Banana", "sentence": "A banana is yellow.", "hint": "B - A - N - A - N - A"},
            {"word": "Grape", "sentence": "Grapes are sweet.", "hint": "G - R - A - P - E"},
        ],
        "colors": [
            {"word": "Red", "sentence": "The rose is red.", "hint": "R - E - D"},
            {"word": "Blue", "sentence": "The sky is blue.", "hint": "B - L - U - E"},
            {"word": "Green", "sentence": "Grass is green.", "hint": "G - R - E - E - N"},
            {"word": "Yellow", "sentence": "The sun is yellow.", "hint": "Y - E - L - L - O - W"},
        ],
        "body": [
            {"word": "Eye", "sentence": "I see with my eye.", "hint": "E - Y - E"},
            {"word": "Ear", "sentence": "I hear with my ear.", "hint": "E - A - R"},
            {"word": "Hand", "sentence": "I write with my hand.", "hint": "H - A - N - D"},
            {"word": "Leg", "sentence": "I run with my legs.", "hint": "L - E - G"},
        ],
        "numbers": [
            {"word": "One", "sentence": "I have one book.", "hint": "O - N - E"},
            {"word": "Two", "sentence": "I have two hands.", "hint": "T - W - O"},
            {"word": "Three", "sentence": "Three birds sat on a tree.", "hint": "T - H - R - E - E"},
            {"word": "Four", "sentence": "Four cats play here.", "hint": "F - O - U - R"},
        ],
    },
    "intermediate": {
        "school": [
            {"word": "Teacher", "sentence": "My teacher is very kind.", "hint": "T - E - A - C - H - E - R"},
            {"word": "Pencil", "sentence": "I write with a pencil.", "hint": "P - E - N - C - I - L"},
            {"word": "Book", "sentence": "I read a good book.", "hint": "B - O - O - K"},
            {"word": "Classroom", "sentence": "We study in the classroom.", "hint": "C - L - A - S - S - R - O - O - M"},
        ],
        "family": [
            {"word": "Mother", "sentence": "My mother cooks food.", "hint": "M - O - T - H - E - R"},
            {"word": "Father", "sentence": "My father goes to work.", "hint": "F - A - T - H - E - R"},
            {"word": "Brother", "sentence": "My brother plays cricket.", "hint": "B - R - O - T - H - E - R"},
            {"word": "Sister", "sentence": "My sister sings a song.", "hint": "S - I - S - T - E - R"},
        ],
        "nature": [
            {"word": "River", "sentence": "The river flows fast.", "hint": "R - I - V - E - R"},
            {"word": "Mountain", "sentence": "The mountain is very tall.", "hint": "M - O - U - N - T - A - I - N"},
            {"word": "Rain", "sentence": "Rain falls from the cloud.", "hint": "R - A - I - N"},
            {"word": "Flower", "sentence": "The flower smells sweet.", "hint": "F - L - O - W - E - R"},
        ],
    },
    "advanced": {
        "science": [
            {"word": "Electricity", "sentence": "Electricity lights up our homes.", "hint": "E - L - E - C - T - R - I - C - I - T - Y"},
            {"word": "Photosynthesis", "sentence": "Plants make food by photosynthesis.", "hint": "P - H - O - T - O - S - Y - N - T - H - E - S - I - S"},
            {"word": "Gravity", "sentence": "Gravity pulls things down.", "hint": "G - R - A - V - I - T - Y"},
        ],
        "environment": [
            {"word": "Pollution", "sentence": "Pollution makes the air dirty.", "hint": "P - O - L - L - U - T - I - O - N"},
            {"word": "Conservation", "sentence": "Conservation saves our forests.", "hint": "C - O - N - S - E - R - V - A - T - I - O - N"},
            {"word": "Biodiversity", "sentence": "Biodiversity means many kinds of life.", "hint": "B - I - O - D - I - V - E - R - S - I - T - Y"},
        ],
    },
}


def get_exercise(level: str, topic: str) -> dict | None:
    """Return a random exercise for the given level and topic."""
    import random
    level = level.strip().lower()
    topic = topic.strip().lower()

    level_data = EXERCISES.get(level, EXERCISES["beginner"])

    # Try the requested topic first, fall back to any available topic
    topic_exercises = level_data.get(topic)
    if not topic_exercises:
        # Pick a random available topic
        available_topics = list(level_data.keys())
        if not available_topics:
            return None
        topic = random.choice(available_topics)
        topic_exercises = level_data[topic]

    exercise = random.choice(topic_exercises)
    return {**exercise, "level": level, "topic": topic}

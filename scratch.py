from src.segmenter import nlp, segment
from src.theme import detect_mood

sentences = [
    "The lion caught the tourist.",
    "Did the lion catch the tourist?",
    "Who caught the tourist?",
    "Catch the tourist!",
    "Let's catch the tourist.",
]

for text in sentences:
    doc = nlp(text)
    clause = segment(text)[0]
    features, conf, reason = detect_mood(clause, doc)
    print(f"{text:35} {sorted(features)}  ({reason})")
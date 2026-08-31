from src.transitivity import analyse_text_transitivity

TESTS = [
    "The lion caught the tourist.",
    "Mary saw the bird.",
    "The music pleased Mary.",
    "Sarah is the treasurer.",
    "There was a storm.",
    "Yesterday she ran quickly in the park.",
]

for text in TESTS:
    print(f"\n{'='*60}\n{text}")
    for a in analyse_text_transitivity(text):
        print(f"\n  Process: {a['process']} ({a['process_lemma']})")
        print(f"  Features: {sorted(a['selection'].features)}")
        print("  Participants:")
        for p in a["participants"]:
            print(f"    {p['role']:12} {p['text']}")
        if a["circumstances"]:
            print("  Circumstances:")
            for c in a["circumstances"]:
                print(f"    {c['feature']:12} {c['text']}")
        print(f"  Confidence: {a['confidence']:.2f}")
        print("  Why:")
        for e in a["evidence"]:
            print(f"    - {e}")
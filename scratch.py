from src.segmenter import nlp, find_clause_heads, assign_spans, find_marker

doc = nlp("He left because he was tired.")
heads = find_clause_heads(doc)
spans = assign_spans(doc, heads)

for h in heads:
    print(f"{h.text:8} marker = {find_marker(h, spans[h.i])}")
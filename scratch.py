from src.segmenter import nlp, find_clause_heads, assign_spans

doc = nlp("The lion caught the tourist because it was hungry.")
heads = find_clause_heads(doc)
spans = assign_spans(doc, heads)

for head_i, tokens in spans.items():
    print(f"{doc[head_i].text:10} -> {' '.join(t.text for t in tokens)}")
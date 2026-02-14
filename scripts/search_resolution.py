import json
from rapidfuzz import fuzz

with open("docs/data.json") as f:
    data = json.load(f)

documents = data.get("documents", [])
target_title = "Strengthening of the coordination of emergency humanitarian assistance of the United Nations"

print(f"Searching for resolution matching: {target_title}")

matches = []
for doc in documents:
    if doc.get("doc_type") == "resolution":
        title = doc.get("title", "")
        if not title:
            continue
        
        # Simple containment check
        if "Strengthening of the coordination" in title:
            print(f"Potential match by containment: {doc['symbol']} - {title}")
            
        score = fuzz.ratio(target_title.lower(), title.lower())
        if score > 50:
            matches.append((doc['symbol'], title, score))

matches.sort(key=lambda x: x[2], reverse=True)
print("\nTop fuzzy matches:")
for m in matches[:5]:
    print(f"{m[2]:.1f}% - {m[0]}: {m[1]}")

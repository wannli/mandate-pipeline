import json
from pathlib import Path

with open("docs/data.json") as f:
    data = json.load(f)

documents = data.get("documents", [])
proposals = [d for d in documents if d.get("doc_type") == "proposal"]
unadopted = [p for p in proposals if not p.get("is_adopted_draft")]

print(f"Total unadopted proposals: {len(unadopted)}")
print("\nUnadopted proposals (Session 80):")
for p in unadopted:
    if p.get("session") == "80":
        print(f"{p['symbol']}: {p['title']}")

import json

with open("docs/data.json") as f:
    data = json.load(f)

doc = next((d for d in data["documents"] if d["symbol"] == "A/RES/80/111"), None)
if doc:
    print(json.dumps(doc, indent=2))
else:
    print("Not found")

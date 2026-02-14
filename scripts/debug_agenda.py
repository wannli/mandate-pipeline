import json

with open("docs/data.json") as f:
    data = json.load(f)

count = 0
for doc in data["documents"]:
    if doc.get("doc_type") == "resolution" and doc.get("session") == "80":
        items = doc.get("agenda_items", [])
        if items:
            print(f"{doc['symbol']}: {items}")
            count += 1
            if count > 5: break

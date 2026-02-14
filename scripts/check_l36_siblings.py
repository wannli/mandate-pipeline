import json

with open("docs/data.json") as f:
    data = json.load(f)

target = "Strengthening of the coordination of emergency humanitarian assistance of the United Nations"

print(f"Checking proposals with title: '{target}'")

for doc in data["documents"]:
    if doc.get("doc_type") == "proposal" and doc.get("session") == "80":
        if target.lower() in doc.get("title", "").lower():
            status = "Adopted" if doc.get("is_adopted_draft") else "Not Adopted"
            adopted_by = f" by {doc.get('adopted_by')}" if doc.get("is_adopted_draft") else ""
            print(f"{doc['symbol']}: {status}{adopted_by}")

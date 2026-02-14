import json

with open("docs/data.json") as f:
    data = json.load(f)

print("Checking resolutions for Agenda Item 72...")

for doc in data["documents"]:
    if doc.get("doc_type") == "resolution" and doc.get("session") == "80":
        # Check text or agenda_items for "72" or "72 (a)"
        # Note: extracted 'agenda_items' might be like ["Item 72"]
        text = str(doc.get("agenda_items", []))
        if "72" in text:
            print(f"{doc['symbol']} - {doc['title']} (Linked: {doc.get('linked_proposals')})")

import json

with open("docs/data.json") as f:
    data = json.load(f)

l3 = next((d for d in data["documents"] if d["symbol"] == "A/80/L.3"), None)
l27 = next((d for d in data["documents"] if d["symbol"] == "A/80/L.27"), None)

if l3:
    print(f"L.3: {l3['title']}")
    print(f"L.3 extracted: {l3.get('is_adopted_draft')}")
else:
    print("L.3 not found")

if l27:
    print(f"L.27: {l27['title']}")
    print(f"L.27 extracted: {l27.get('is_adopted_draft')}")
    if l27.get('is_adopted_draft'):
        print(f"L.27 adopted by: {l27.get('adopted_by')}")
else:
    print("L.27 not found")

import json
from pathlib import Path

# Load data
data_path = Path("docs/data.json")
if not data_path.exists():
    print("docs/data.json not found")
    exit(1)

with open(data_path) as f:
    data = json.load(f)

documents = data.get("documents", [])
proposals = [d for d in documents if d.get("doc_type") == "proposal"]
resolutions = [d for d in documents if d.get("doc_type") == "resolution"]

print(f"Total documents: {len(documents)}")
print(f"Total proposals: {len(proposals)}")
print(f"Total resolutions: {len(resolutions)}")

# Check adopted status
adopted_proposals = [p for p in proposals if p.get("is_adopted_draft")]
print(f"Adopted proposals: {len(adopted_proposals)}")
print(f"Adoption rate: {len(adopted_proposals) / len(proposals) * 100:.1f}%")

# Check linked resolutions
linked_resolutions = [r for r in resolutions if r.get("linked_proposals")]
print(f"Resolutions with linked proposals: {len(linked_resolutions)}")
print(f"Linkage rate: {len(linked_resolutions) / len(resolutions) * 100:.1f}%")

# Sample some adopted proposals
print("\nSample adopted proposals:")
for p in adopted_proposals[:5]:
    print(f"  {p['symbol']} -> {p.get('adopted_by')}")

# Sample some unadopted proposals
print("\nSample unadopted proposals (potential misses):")
for p in [p for p in proposals if not p.get("is_adopted_draft")][:5]:
    print(f"  {p['symbol']}")

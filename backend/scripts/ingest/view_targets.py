import json

with open('backend/data/civictech_coi.json', 'r', encoding='utf-8') as f:
    civic = json.load(f)

civic_map = {str(a.get('article')).strip().upper(): a for a in civic}
targets = ['39A', '44', '51A', '226']
for t in targets:
    item = civic_map.get(t)
    print('=== ARTICLE ' + t + ': ' + item.get('title', '') + ' ===')
    print(item.get('description', ''))
    print()

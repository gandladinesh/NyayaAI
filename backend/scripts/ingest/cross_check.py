import json
import re

with open('backend/data/raw_coi.json', 'r', encoding='utf-8') as f:
    yash_data = json.load(f)[0]

with open('backend/data/civictech_coi.json', 'r', encoding='utf-8') as f:
    civic_data = json.load(f)

yash_map = {str(a.get('ArtNo')).strip().upper(): a for a in yash_data}
civic_map = {str(a.get('article')).strip().upper(): a for a in civic_data}

common_targets = [
    '12', '13', '14', '15', '16', '17', '18', '19', '20',
    '21', '21A', '22', '23', '24', '25', '26', '27', '28',
    '29', '30', '32'
]

def norm(s):
    s = re.sub(r'[\u201c\u201d\u2018\u2019\'\"]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

print('Cross-check comparison between Yash-Handa and civictech datasets:')
for t in common_targets:
    y_art = yash_map.get(t)
    c_art = civic_map.get(t)
    if not y_art or not c_art:
        print(f'Art {t}: Missing in one dataset (Yash: {bool(y_art)}, Civic: {bool(c_art)})')
        continue
    
    y_desc = y_art.get('ArtDesc', '').strip()
    c_desc = c_art.get('description', '').strip()
    
    match = norm(y_desc) == norm(c_desc)
    print(f'Art {t}: Match={match} (Yash len: {len(y_desc)}, Civic len: {len(c_desc)})')
    if not match:
        print('   Yash: ', norm(y_desc)[:90])
        print('   Civic:', norm(c_desc)[:90])

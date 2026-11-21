import json
print(json.dumps({'findings': [{'rule': 'line-width', 'category': 'reflow', 'path': '.prettierrc.json', 'message': 'width 100', 'fixable': True}]}))

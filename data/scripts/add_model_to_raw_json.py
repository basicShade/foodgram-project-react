import json
import sys

try:
    source = sys.argv[1]
    appmodel = sys.argv[2]

    with open(f'{source}', encoding='utf8') as f:
        d = json.load(f)
        result = []
        for i, item in enumerate(d):
            row = {}
            row['model'] = str(appmodel)
            row['pk'] = i+1
            row['fields'] = item
            result.append(row)

        with open(f'{appmodel}_dump.json', 'w', encoding='utf8') as w:
            json.dump(result, w, ensure_ascii=False)
except IndexError:
    print('Укажите исходный файл <file.json> и название модели <app.model>')



import os
import re

for root, _, files in os.walk('d:/ibmjulybob/loreweave/backend/app/schemas'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f), 'r') as file:
                content = file.read()
                matches = re.findall(r'([A-Z][a-zA-Z]+(?:Status|Type|Direction))\.([A-Za-z0-9_]+)', content)
                for m in set(matches):
                    print(f"{f}: {m[0]}.{m[1]}")

import os
import re

for root, _, files in os.walk('d:/ibmjulybob/loreweave/backend/app'):
    for f in files:
        if f.endswith('.py'):
            with open(os.path.join(root, f), 'r') as file:
                content = file.read()
                matches = re.findall(r'from\s+app\.models\.([a-z_]+)\s+import\s+\(?(.*?)\)?(?:$|\n\n)', content, re.DOTALL | re.MULTILINE)
                for model, imports in matches:
                    imports = [i.strip() for i in imports.replace('\n', ' ').split(',')]
                    for i in imports:
                        if i and i != '(':
                            print(f"{model}: {i}")

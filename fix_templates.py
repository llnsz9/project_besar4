import os
import re

template_dir = 'templates'
for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        path = os.path.join(template_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '{% load static %}' not in content:
            content = '{% load static %}\n' + content
            
        def replacer(match):
            attr = match.group(1)
            val = match.group(2)
            if not val.startswith(('http', '/', '{%', '#', 'mailto:')):
                return f'{attr}="{{% static \'{val}\' %}}"'
            return match.group(0)
            
        content = re.sub(r'(href|src)="([^"]+)"', replacer, content)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Templates updated.")

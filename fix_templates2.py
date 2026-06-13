import os

template_dir = 'templates'
for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        path = os.path.join(template_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace("{% static 'login.html' %}", "/login.html")
        content = content.replace("{% static 'register.html' %}", "/register.html")
        content = content.replace("{% static 'index.html' %}", "/")
        content = content.replace("{% static 'dashboard.html' %}", "/dashboard.html")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

print("Links fixed.")

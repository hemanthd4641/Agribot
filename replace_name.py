import os

replacements = {
    "Raitha mitra": "Raitha mitra",
    "Raitha mitra": "Raitha mitra",
    "Raitha mitra": "Raitha mitra",
    "Raitha mitra": "Raitha mitra",
    "raithamitra": "raithamitra",
    "raithamitra-assistant": "raitha-mitra",
}

root_dir = r"c:\Users\heman\Downloads\LLM_Agri_Bot-main\LLM_Agri_Bot-main"

for root, dirs, files in os.walk(root_dir):
    # skip .git, venv, pycache
    if any(ignore in root for ignore in ['.git', 'venv', '__pycache__', 'node_modules']):
        continue
    for f in files:
        if not f.endswith(('.py', '.html', '.js', '.css', '.md', '.webmanifest', '.env', '.example', '.txt')):
            continue
            
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
        except:
            continue
            
        new_content = content
        for k, v in replacements.items():
            new_content = new_content.replace(k, v)
            
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f"Updated {path}")

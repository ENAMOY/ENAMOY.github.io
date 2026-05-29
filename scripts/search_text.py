
import os

skip_dirs = {'.git', '.venv', 'node_modules', 'backup_original', 'chrome-devtools-mcp'}
found = False

print("Searching for '项目地址'...")

for root, dirs, files in os.walk('.'):
    # Prune skipped directories
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for file in files:
        if file.endswith(('.html', '.md', '.py', '.js', '.css', '.txt')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if '项目地址' in content:
                        print(f'FOUND in: {path}')
                        found = True
            except Exception as e:
                pass

if not found:
    print('NOT FOUND in any searched file.')

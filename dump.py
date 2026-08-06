import re

try:
    with open('error_source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print('--- PASSWORD INPUTS ---')
    for match in re.finditer(r'<input[^>]*type="password"[^>]*>', html):
        print(match.group(0))
        
    print('--- VERIFY BUTTONS ---')
    for match in re.finditer(r'<button[^>]*>.*?Verify.*?</button>', html):
        print(match.group(0))
except Exception as e:
    print(e)

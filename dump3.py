import re
try:
    with open('error_source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    title = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
    print('Title:', title.group(1).strip() if title else 'No title')
except Exception as e:
    print(e)

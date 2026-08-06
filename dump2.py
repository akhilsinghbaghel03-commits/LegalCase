import re
try:
    with open('error_source.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print('--- OTP INPUTS ---')
    for match in re.finditer(r'<input[^>]*id="[^"]*OTP[^"]*"[^>]*>', html):
        print(match.group(0))
        
    print('--- VERIFY TEXT ---')
    for match in re.finditer(r'(.{0,20})Verify(.{0,20})', html):
        print(match.group(0))
except Exception as e:
    print(e)

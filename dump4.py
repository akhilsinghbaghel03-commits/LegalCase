import re
with open(r'test\run_signup.py', 'r', encoding='utf-8') as f:
    code = f.read()

for match in re.finditer(r'raise Exception\("Failed to verify.*?after 3 attempts\."\)', code):
    print(match.group(0))

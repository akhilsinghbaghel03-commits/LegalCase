import sys

filepath = 'test/run_signup.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '# 9. Verify Final Dashboard' in line:
        start_idx = i
    if 'print("Error in post-login checks: {e}")' in line:
        end_idx = i - 1
        break

if start_idx != -1 and end_idx != -1:
    for i in range(start_idx, end_idx + 1):
        if lines[i].startswith('    '):
            lines[i] = lines[i][4:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed indentation successfully.")
else:
    print("Could not find bounds.")

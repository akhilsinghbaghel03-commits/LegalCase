import re

with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'# 4\. Click Save Button.*?time\.sleep\(2\)', text, re.DOTALL)
if match:
    old_code = match.group(0)
    print('Found it!')
    new_code = '''# 4. Click Save Button (for the modal)
                    print("Clicking Save for the new tag modal...")
                    try:
                        save_btns = driver.find_elements(By.XPATH, "//button[contains(translate(., 'SAVE', 'save'), 'save')]")
                        visible_saves = [btn for btn in save_btns if btn.size['width'] > 0 and btn.size['height'] > 0]
                        # Only click if there's more than 1 save button (otherwise we might prematurely click the main form's Save button!)
                        if len(visible_saves) > 1:
                            # Click the last visible save button (which is typically the one in the top-most modal)
                            driver.execute_script("arguments[0].click();", visible_saves[-1])
                            time.sleep(2)
                        else:
                            print("Note: Only 1 save button found. Assuming tag auto-saved or no modal save button exists.")'''
    new_text = text.replace(old_code, new_code)
    with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Replaced')
else:
    print('Not found')

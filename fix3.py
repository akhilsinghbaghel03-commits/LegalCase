import re

with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'# 4\. Click Save Button.*?print\(f"Warning: Could not click modal save button: \{e\}"\)', text, re.DOTALL)
if match:
    old_code = match.group(0)
    print('Found it!')
    new_code = '''# 4. Click Save Button (for the modal)
                    print("Clicking Save/Close for the new tag modal...")
                    try:
                        # Only look for a save button inside a popup/modal container
                        save_btns = driver.find_elements(By.XPATH, "//div[contains(@class, 'popup') or contains(@class, 'modal') or contains(@class, 'dialog') or @role='dialog']//button[contains(translate(., 'SAVE', 'save'), 'save')]")
                        visible_saves = [btn for btn in save_btns if btn.size['width'] > 0 and btn.size['height'] > 0]
                        
                        if visible_saves:
                            driver.execute_script("arguments[0].click();", visible_saves[-1])
                            time.sleep(2)
                        else:
                            print("Note: No modal save button found. Trying to send ESC to close modal just in case.")
                            from selenium.webdriver.common.keys import Keys
                            try:
                                from selenium.webdriver.common.action_chains import ActionChains
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                time.sleep(1)
                            except Exception: pass
                    except Exception as e:
                        print(f"Warning: Could not handle modal save/close: {e}")'''
    new_text = text.replace(old_code, new_code)
    with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Replaced')
else:
    print('Not found')

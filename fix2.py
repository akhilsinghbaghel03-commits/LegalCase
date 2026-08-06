with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad_code = '''                        else:
                            print("Note: Only 1 save button found. Assuming tag auto-saved or no modal save button exists.")'''

good_code = '''                        else:
                            print("Note: Only 1 save button found. Assuming tag auto-saved or no modal save button exists.")
                    except Exception as e:
                        print(f"Warning: Could not click modal save button: {e}")'''

new_text = text.replace(bad_code, good_code)
with open(r'c:\Users\dell\Akhil_AI\test\run_signup.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Fixed!')

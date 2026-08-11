import time
from test.utils.helpers import get_driver

driver, wait = get_driver()
driver.get("https://yorpro-test.outsystems.app/legalhub/signup")
time.sleep(15)
html = driver.page_source
with open("signup_page.html", "w", encoding="utf-8") as f:
    f.write(html)
driver.quit()

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

driver.get("https://www.peacefmonline.com/")

print(
    driver.title
)

search = driver.find_element(By.NAME, "q")
search.send_keys("test")
search.send_keys(Keys.RETURN)

print(driver.page_source)
time.sleep(5)

driver.quit()

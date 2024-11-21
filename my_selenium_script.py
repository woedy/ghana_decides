import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()

driver.get("https://ghanaelections.peacefmonline.com/pages/2020/parliament/ahafo/")

print(
    driver.title
)

elements = driver.find_elements(By.CLASS_NAME, "e_res_list1-npp")  # Note: find_elements instead of find_element

for element in elements:
    print(element.text)

time.sleep(5)

driver.quit()

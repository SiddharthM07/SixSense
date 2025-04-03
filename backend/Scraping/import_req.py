from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_path = "/usr/bin/google-chrome"  # Update this if needed
chrome_driver_path = "/usr/bin/chromedriver"  # Update this if needed

options = Options()
options.binary_location = chrome_path  # Manually set Chrome binary location

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://www.google.com")
print(driver.title)
driver.quit()

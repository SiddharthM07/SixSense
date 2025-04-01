from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Specify the paths
chrome_path = "/usr/bin/google-chrome"  # Your Google Chrome binary
chrome_driver_path = "/usr/bin/chromedriver"  # Check if this is correct

# Set up Chrome options
options = Options()
options.binary_location = chrome_path  # Manually set Chrome binary location
options.add_argument(
    "--headless"
)  # Run Chrome in headless mode (remove if you want a visible browser)
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Initialize Chrome WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Open a website and print the title
driver.get("https://www.google.com")
print("Page Title:", driver.title)

# Close the browser
driver.quit()

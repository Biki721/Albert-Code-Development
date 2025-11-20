from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

webdriver_path="Webdrivers\\chromedriver.exe"
driver=webdriver.Chrome(executable_path=webdriver_path)
driver.close()
driver.close()
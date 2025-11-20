from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.keys import Keys
import time
import os
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from pywinauto.findwindows import find_windows
# from openai import AzureOpenAI
# from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, ElementNotSelectableException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from SelectCertificate import authenticate_with_certificate

## psnow
link_psnow = 'https://psnow.ext.hpe.com/#/'
# chrome_options = Options()
# # chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
# chrome_options.add_argument("--disable-gpu")
# # chrome_options.add_argument('--ignore-certificate-errors')
# webdriver_path = "Webdrivers\\chromedriver.exe"
# service = Service(webdriver_path)
# driver = webdriver.Chrome(service=service)
# driver.maximize_window()    
# driver.maximize_window()
# wait = WebDriverWait(driver, 120, ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])
def setUp():
    global driver, wait
    webdriver_path = "Webdrivers\\chromedriver.exe"
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 120, ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])
    

def check_psnow_login(driver,link_psnow,wait,user,password):
    driver.get(link_psnow)
    # print(xpathlist[5][1],xpathlist[5][6])
     # print(xpathlist[5][1],type(xpathlist[5][1]),user,'*******')    
    # time.sleep(40)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="request-partner-button"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="oktaEmailInput"]'))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="oktaSignInBtn"]'))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="password-sign-in"]'))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onepass-submit-btn"]'))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][6]))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][7]))).click()
    time.sleep(10)
    try:
        authenticate_with_certificate('BOT DEC-D001a') # select certificate
    except:
        print('\nNO CERTIFICATE SELECTION\n')
        try:
            authenticate_with_certificate('BOT DEC-D001a') # select certificate
        except Exception as e:
            print(str(e))
    time.sleep(5) 

setUp()

# Path to your ChromeDriver (make sure this matches the Chrome version)
check_psnow_login(driver,link_psnow,wait,'bot.dec-d001a@hpe.com','Login2PRP!')
driver.get(link_psnow)


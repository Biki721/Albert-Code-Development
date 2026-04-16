from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
import work
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from inscriptis import get_text
from SelectCertificate import authenticate_with_certificate
from bs4 import BeautifulSoup
import pandas as pd

webdriver_path = "Webdrivers\\chromedriver.exe"
service = Service(webdriver_path)
driver = webdriver.Chrome(service=service)
driver.maximize_window()
time.sleep(5)

excel_file_path = 'Error messages for external URL\Error messages for external URL..xlsx.xlsx'
sheet_name = 'Error_message'
df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
Errormsg = df['message'].tolist() 
Errormsg = [s.strip() for s in Errormsg if s != '']
errorlinks_seismic=[]

def check_seismic_error(driver,url,Errorlink,Errormsg):
    driver.get(url)
    driver.find_element(By.ID, 'oktaEmailInput').send_keys(user)
    driver.find_element(By.ID, 'oktaSignInBtn').click()
    time.sleep(5)
    driver.find_element(By.ID, 'password-sign-in').send_keys(password)
    driver.find_element(By.ID, 'onepass-submit-btn').click()
    time.sleep(5)
    driver.get(Errorlink)
    time.sleep(5)
    driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div/div/div/div/div[3]/div[2]/button[1]').click()
    time.sleep(5)
    driver.get(Errorlink)
    time.sleep(10)

    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    print(text_content)
    print(type(text_content))
    print(Errormsg)
    found_text = False

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    return found_text
# if not found_text:
#     print("Text not found")
url = "https://partner.hpe.com"
user = "mapdummypartner@yopmail.com"
password = "Login2PRP!"
Errorlink = "https://hpe.seismic.com/Link/Content/DCUpRgoJiMjUK2YDpUIjOCZg"

URL_error = check_seismic_error(driver,url,Errorlink,Errormsg)
if URL_error:
    print(URL_error)
    errorlinks_seismic.append(Errorlink)
print(errorlinks_seismic)     

# time.sleep(10)
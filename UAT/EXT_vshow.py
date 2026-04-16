import pandas as pd
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions as EC
import work 
import openpyxl
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from inscriptis import get_text
from SelectCertificate import authenticate_with_certificate
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, ElementNotSelectableException, WebDriverException, TimeoutException

# webdriver_path = "Webdrivers\\chromedriver.exe"
# service = Service(webdriver_path)
# driver = webdriver.Chrome(service=service)
# driver.maximize_window()


# excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
# sheet_name = 'Error_message'
# df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
# Errormsg = df['message'].tolist() 
# Errormsg= [s.strip() for s in Errormsg if s != '']
# wait = WebDriverWait(driver,30,ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])
# errorlinks_VS=[]

def check_vs_login(driver,url_VS,wait,xpathlist,user,password):
    driver.get(url_VS)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][3]))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, xpathlist[2][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][5]))).click()
    time.sleep(5)
def check_vs_error(driver,url_VS,Errormsg):
    driver.get(url_VS)

    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    print(type(text_content))
    time.sleep(10)

    # print(Errormsg)
    found_text = False
    time.sleep(10)

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    return found_text

    # if not found_text:
    #     print("Text not found")
if __name__=='__main__':
    url_VS = "http://vshow.on24.com/vshow/HPETekTalks/exhibits/WebinarListing"
    user = "mapdummypartner@yopmail.com"
    password = "Login2PRP!"
    URL_error=check_vs_error(driver,url_VS,Errormsg)
    if URL_error:
        errorlinks_VS.append(url_VS)
    print(errorlinks_VS)         


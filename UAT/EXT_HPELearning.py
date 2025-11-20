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
# time.sleep(5)


# excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
# sheet_name = 'Error_message'
# df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
# Errormsg = df['message'].tolist() 
# Errormsg = [s.strip() for s in Errormsg if s != '']
# errorlinks_hpe_leraning=[]
# wait = WebDriverWait(driver,30,ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])

def check_learning_login(driver,url_hpelearn,wait,xpathlist,user,password):
    driver.get(url_hpelearn)    
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[3][1]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[3][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH,xpathlist[3][3]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[3][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[3][5]))).click()
    time.sleep(10)

def check_learning_error(driver,url_hpelearn,Errormsg):
    driver.get(url_hpelearn)

    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(20)

    Errormsg = work.doc_reader("Externallink_Error_Message.docx")
    Errormsg = [s.strip() for s in Errormsg if s != '']
    # print(Errormsg)
    found_text = False

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    print(found_text) 
    return found_text 
   

# if not found_text:
#     print("Text not found")
if __name__=='__main__':
    url_hpelearn = "http://www.mylearninghpe.com/"
    user = "mapdummypartner@yopmail.com"
    password = "Login2PRP!"
    URL_error=check_learning_error(driver,url_hpelearn,Errormsg,wait)
    print(URL_error)
    if URL_error:
        errorlinks_hpe_leraning.append(url_hpelearn)
    print(errorlinks_hpe_leraning)     

# time.sleep(10)
# from xml.etree.ElementPath import xpath_tokenizer
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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, ElementNotSelectableException, WebDriverException, TimeoutException


# webdriver_path = "Webdrivers\\chromedriver.exe"
# service = Service(webdriver_path)
# driver = webdriver.Chrome(service=service)
# driver.maximize_window()

# excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
# sheet_name = 'Error_message'
# df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
# Errormsg = df['message'].tolist() 
# Errormsg = [s.strip() for s in Errormsg if s != '']
# errorlinks_Psnow=[]
# wait = WebDriverWait(driver,30,ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])

def check_psnow_login(driver,errlink_psnow,wait,xpathlist,user,password):
    driver.get(errlink_psnow)
    # print(xpathlist[5][1],type(xpathlist[5][1]),user,'*******')    
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][1]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][3]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][5]))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][6]))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][7]))).click()
time.sleep(5)

def check_psnow_error(driver,errlink_psnow,Errormsg):
    driver.get(errlink_psnow)
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(5)

    # print(Errormsg)
    found_text = False

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    return found_text    

    # if not found_text:
    #     print("Text not found")
    
    if __name__=='__main__':  
        errlink_psnow = "https://psnow.ext.hpe.com/"
        user = "mapdummypartner@yopmail.com"
        password = "Login2PRP!"
        URL_error=check_psnow_error(driver,errlink_psnow,Errormsg)
        if URL_error:
            print(URL_error)
            errorlinks_Psnow.append(errlink_psnow)
        print(errorlinks_Psnow)    

# time.sleep(10)
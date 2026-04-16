from xml.etree.ElementPath import xpath_tokenizer_re
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
# wait = WebDriverWait(driver, 60, ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])
# print(Errormsg)

errorlinks_seismic=[]
xpathlist=[]
# slink = xpathlist[1][0]
# print(xpathlist)

def check_seismic_login(driver,seis_login_link,wait,xpathlist,user,password):
    driver.get(seis_login_link)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][1]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH,xpathlist[1][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][3]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH,xpathlist[1][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][5]))).click()
    time.sleep(10)
    # driver.get(seislink)
    # time.sleep(10)
def check_seismic_error(driver,seislink,Errormsg):
    driver.get(seislink)
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][1]))).click()
    time.sleep(10)
    # print(Errormsg)
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(20)

    found_text = False
    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    print(found_text)    
    # Error=errorlinks_seismic.append(url2pathname)    
    return found_text      
    if not found_text:
        print("Text not found")

# if __name__=='__main__':

    Base_url = "https:///partner.hpe.com"
    user = "mapdummypartner@yopmail.com"
    password = "Login2PRP!"
    seislink = "http://hpe.seismic.com/Link/Content/DCiVelsODZDkyC_RdTBYe6tQ"
   
    URL_error=check_seismic_error(driver,Base_url,seislink,Errormsg)
    if URL_error:
        print(URL_error)
        errorlinks_seismic.append(seislink)
    print(errorlinks_seismic) 
    # time.sleep(10)
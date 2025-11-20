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
def check_seismic_login(driver,seis_login_link,wait,xpathlist,user,password):

    
    driver.get(seis_login_link)
    time.sleep(10)
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div/div[2]/div/div[1]/div/div[1]/div/main/div[2]/div[1]/ul/li[2]/button'))).click()
    
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][1]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH,xpathlist[1][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][3]))).click()
    wait.until(EC.element_to_be_clickable((By.XPATH,xpathlist[1][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][5]))).click()
    # try:
    #     authenticate_with_certificate('BOT DEC-D001a') # select certificate
    # except:
    #     print('\nNO CERTIFICATE SELECTION\n')
    #     try:
    #         authenticate_with_certificate('BOT DEC-D001a') # select certificate
    #     except Exception as e:
    #         print(str(e))

    time.sleep(20)
    try:
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form19"]/div[2]/div[2]/div[2]/a')))
        elem.click()
        time.sleep(20) 
    except:
        pass



    
    # driver.get(seislink)
    # time.sleep(10)
def check_seismic_error(driver,wait,xpathlist,seislink,Errormsg):
    driver.get(seislink)
    # #wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][1]))).click()
    time.sleep(10)
    try: 
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[1][1]))).click()
    except:
        pass
    # print(Errormsg)
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(10)

    found_text = False
    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    print(found_text)    
    # Error=errorlinks_seismic.append(url2pathname)    
    return found_text  

def check_psnow_login(driver,errlink_psnow,wait,xpathlist,user,password):
    driver.get(errlink_psnow)
    # print(xpathlist[5][1],xpathlist[5][6])
     # print(xpathlist[5][1],type(xpathlist[5][1]),user,'*******')    
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][1]))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][2]))).send_keys(user)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][3]))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][4]))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][5]))).click()
    except Exception as e:
        print(str(e))
    time.sleep(20)
    try:
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form19"]/div[2]/div[2]/div[2]/a')))
        elem.click()
        time.sleep(20) 
    except:
        pass
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][6]))).click()
    # wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[5][7]))).click()
    # try:
    #     authenticate_with_certificate('BOT DEC-D001a') # select certificate
    # except:
    #     print('\nNO CERTIFICATE SELECTION\n')
    #     try:
    #         authenticate_with_certificate('BOT DEC-D001a') # select certificate
    #     except Exception as e:
    #         print(str(e))
    # time.sleep(5)        

def check_psnow_error(driver,errlink_psnow,wait,xpathlist,Errormsg):
    driver.get(errlink_psnow)
    time.sleep(10)
    try:
        button_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpathlist[5][1])))
        button_element.click()
    except TimeoutException:
        print("Element not found 1.")

    try:
        button_element1 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpathlist[5][6])))
        button_element1.click()
    except TimeoutException:
        print("Element not found 2.")
    try:
        button_element1 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpathlist[5][7])))
        button_element1.click()
    except TimeoutException:
        print("Element not found 3.")
    
    # button_element1 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpathlist[5][6])))
    # if button_element1.is_enabled():
    #     button_element1.click()
    # else:
    #     print("not available")

    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(20)

    # print(Errormsg)
    found_text = False

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    print(found_text)
    return found_text 
    
def check_learning_login(driver,url_hpelearn,wait,xpathlist,user,password):
    driver.refresh()
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
    time.sleep(10)

    for msg in Errormsg:
        if msg in text_content:
            print(msg)
            found_text = True
            break
    print (found_text)
    return found_text
        
def check_vs_login(driver,url_VS,wait,xpathlist,user,password):
    driver.get(url_VS)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][2]))).send_keys(user)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][3]))).click()
    wait.until(EC.visibility_of_element_located((By.XPATH, xpathlist[2][4]))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.XPATH, xpathlist[2][5]))).click()
    time.sleep(20)
    try:
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form19"]/div[2]/div[2]/div[2]/a')))
        elem.click()
        time.sleep(20) 
    except:
        pass
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
    print(found_text)
    return found_text


def check_certification_error(driver,url_certification,Errormsg):
    driver.get(url_certification)
      
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    # print(text_content)
    # print(type(text_content))
    time.sleep(20)    
    found_text = False
    print(found_text)
    time.sleep(10)

    for msg in Errormsg:
        if msg in text_content:
        
            print(msg)
            found_text = True            
            break
    return found_text

    # if not found_text:
    #     print("Text not found")
    url_certification = "https://certification-learning.hpe.com/ext/certifications"
    URL_error=check_certif_error(driver,url_certification,Errormsg)
    if URL_error:
        print(URL_error)
        errorlinks_certification.append(url_certification)
    print(errorlinks_certification)    


# if __name__=='__main__':  
#         errlink_psnow = "https://psnow.ext.hpe.com/"
#         user = "mapdummypartner@yopmail.com"
#         password = "Login2PRP!"
#         URL_error=check_psnow_error(driver,errlink_psnow,Errormsg)
#         if URL_error:
#             print(URL_error)
#             errorlinks_Psnow.append(errlink_psnow)
#         print(errorlinks_Psnow)  
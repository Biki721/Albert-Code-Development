import pandas as pd
from os import listdir
from os.path import isfile, join
import os
import openpyxl
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, ElementNotSelectableException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from itertools import count
from selenium import webdriver
import numpy as np
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
import work
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# url = "https://partner.hpe.com"
# user = "mapdummypartner@yopmail.com"
# password = "Login2PRP!"

# webdriver_path = "Webdrivers\\chromedriver.exe"
# service = Service(webdriver_path)
# driver = webdriver.Chrome(service=service)
# driver.get(url)
# driver.maximize_window()
# time.sleep(5)

# user_element = driver.find_element(By.ID, 'oktaEmailInput').send_keys(user)
# sign_in_button = driver.find_element(By.ID, 'oktaSignInBtn').click()
# time.sleep(10)
# password_element = driver.find_element(By.ID, 'password-sign-in').send_keys(password)
# sign_in_button = driver.find_element(By.ID, 'onepass-submit-btn').click()
# time.sleep(10)

# url2pathname='https://hpe.seismic.com/app#/error/404'
# driver.get(url2pathname)
# time.sleep(5)
# driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div/div/div/div/div[3]/div[2]/button[1]').click()
# time.sleep(5)
# driver.get(url2pathname)
# time.sleep(120)

# page_content = driver.page_source
# soup = BeautifulSoup(page_content, 'html.parser')
# text_content = soup.get_text()
# # print(text_content)
# # print(type(text_content))

# excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
# sheet_name = 'Error_message'
# df_errmsg = pd.read_excel(excel_file_path, sheet_name=sheet_name)
# Errormsg = df_errmsg['message'].tolist() 
# Errormsg = [s.strip() for s in Errormsg if s != '']
# # print(Errormsg)s

filename = "Error messages for external URL\Error messages for external URL.xlsx"
xpathlist = []
wb = openpyxl.load_workbook(filename)
worksheet = wb.active
 
for row in worksheet.iter_rows():
    row_values = []
    for cell in row:
        row_values.append(cell.value)
    xpathlist.append(row_values)
wb.close() 
print("list of xpath*****************",xpathlist)
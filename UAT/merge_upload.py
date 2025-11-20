from calendar import week
import time
import datetime 
import numpy as np
import pandas as pd
import os
from pandas._libs.tslibs import NaTType
import pyautogui
import math
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from SelectCertificate import authenticate_with_certificate, handle_pin_prompt
import VaultSample as vs
from selenium.webdriver.chrome.service import Service
from language_utils import normalize_language

pyautogui.FAILSAFE = False

dff=pd.read_excel("Schedule.xlsx")
lang = list(dff['Language'])

#print(lang)
week_no = vs.printweeknumber()
#print(week_no)
lang_weeknumber=dict(zip(lang,week_no))
#print(lang_weeknumber)
#print("**************************")
#print(lang_weeknumber)
#lang_runnumber={'French':1,'German':2,'Spanish':3,'Russian':1,'Turkish':2,'Portugese':3,'Chinese':3,'Korean':2,'Italian':1,'Japanese':1,'Singaporean':2,'Indonesian':3,'Taiwan':1,'English':2,'LARSpanish':3}
to_be_merged_folderpath = "Reports"
to_be_uploaded_filepath='D:\\UAT\\WA Reports\\Aggregated Report.xlsx'

# dir_list_upload = os.listdir(folderpath)

def generate_session_id(lang):
    lang = normalize_language(lang)

    if isinstance(lang,str):
        weeknumber = str(int(lang_weeknumber[lang]))    
    year = datetime.datetime.now().year
    session_id = str(year) + "_" + weeknumber  # Only return the first session ID
    return session_id



def aggregate(path):
    dir_list = os.listdir(path)
    excl_list=[]
    for file in dir_list:
        if not pd.read_excel(path+"/"+file, engine='openpyxl').empty:
            excl_list.append(pd.read_excel(path+"/"+file))
    excl_merged = pd.DataFrame()
    for excl_file in excl_list:
        excl_merged = excl_merged._append(excl_file, ignore_index=False)
    if (excl_merged.empty):
        excl_merged.to_excel(r'WA Reports/Aggregated Report.xlsx', index=False)
        excl_list.clear()
        clear_folder(to_be_merged_folderpath)
        return
    try:
        #print("BEFORE",excl_merged)
        excl_merged= excl_merged[excl_merged.columns.drop(list(excl_merged.filter(regex='Issue')))]
        excl_merged= excl_merged[excl_merged.columns.drop(list(excl_merged.filter(regex='Unnamed')))]
        excl_merged.insert(loc=0, column='Issue ID', value=np.arange(len(excl_merged)))
        #print(excl_merged)
        excl_merged=excl_merged.dropna(thresh=4)
    except:
        pass
    #print("WOHOO",excl_merged)
    language=[normalize_language(lang) for lang in list(excl_merged['Language'])]

    #print(language)
  
    # runnumber=[str(lang_runnumber[lang]) for lang in language if type(lang)==str]
    # print('*****',lang_weeknumber)
    
    print(lang_weeknumber.keys())

    #weeknumber=[str(lang_weeknumber[lang]) for lang in language if type(lang)==str]
    weeknumber=[str(lang_weeknumber[lang]) for lang in language if type(lang)==str]
    
    #weeknumber = [str(week_no[0]) for i in range(len(lang))]
    excl_merged['Time Identified'] = pd.to_datetime(excl_merged['Time Identified'])
    date=list(excl_merged['Time Identified'])
    date=[t.strftime('%d/%m/%Y') for t in date if not type(t)==NaTType]
    year=datetime.datetime.now().year

    session_id=[str(year)+"_"+weeknumber[i] for i in range(len(weeknumber))]
    # print(session_id,len(session_id))

    
    excl_merged.insert(loc=1, column='Session ID', value=session_id)
    excl_merged.to_excel('WA Reports/Aggregated Report.xlsx', index=False)
    excl_list.clear()
    clear_folder(to_be_merged_folderpath)

    
def upload(filepath):
    webdriver_path = 'Webdrivers\\chromedriver.exe'
    service = Service(webdriver_path)
    driver=webdriver.Chrome()
    # driver.maximize_window() 
    wait = WebDriverWait(driver,10,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])

    driver.get(r'https://hpe.sharepoint.com/teams/Albert/Shared%20Documents/Forms/AllItems.aspx?viewid=9a972322%2D2dd5%2D4d5f%2Da761%2Ddf9bc422ecb1&id=%2Fteams%2FAlbert%2FShared%20Documents%2FAggregated%20Report%20Files')
    wait.until(EC.element_to_be_clickable((By.ID, "i0116"))).send_keys('biki.dey@hpe.com')
    # wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9"))).click()
    time.sleep(12)
    # try:
    #     authenticate_with_certificate('BOT DEC-D001a')
    # except Exception as e:
    #     print(str(e))
    #     try:
    #         authenticate_with_certificate('BOT DEC-D001a')
    #     except Exception as e:
    #         print(str(e)) 
    #handle_pin_prompt('04021999')
    wait.until(EC.element_to_be_clickable((By.ID, "idBtn_Back"))).click()
    time.sleep(10)
    wait.until(EC.element_to_be_clickable((By.NAME, "Upload"))).click()
    wait.until(EC.element_to_be_clickable((By.NAME, "Files"))).click()
    time.sleep(3)
    #authenticate_with_certificate('jhhjjhj')
    #handle_pin_prompt('87979')
    #wait.until(EC.element_to_be_clickable((By.ID, "idBtn_Back"))).click()
    #print(driver.page_source)
  
    time.sleep(1)
    pyautogui.write(filepath, interval=0.25)
    pyautogui.press('Enter')
    time.sleep(10)
    driver.close()

def clear_folder(path):
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


if __name__ == '__main__':
    # print(type(generate_session_id('English')))
    # aggregate(to_be_merged_folderpath)
    upload(to_be_uploaded_filepath)
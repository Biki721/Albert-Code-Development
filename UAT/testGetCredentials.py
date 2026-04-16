import pandas as pd
from os import listdir
from os.path import isfile, join
import os
import glob
import openpyxl
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotVisibleException, ElementNotSelectableException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from itertools import count
from selenium import webdriver
import numpy as np
import time
from selenium.webdriver.support import expected_conditions as EC
import work
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import Seismic
import EXT_Psnow
import EXT_HPELearning
import EXT_certification
import EXT_vshow
class PRP():
    Base_url = "https://partner.hpe.com"
    user = "mapdummypartner@yopmail.com"
    password = "Login2PRP!"

    webdriver_path = "Webdrivers\\chromedriver.exe"
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 60, ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])

    excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
    sheet_name = 'Error_message'
    df_errmsg = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    Errormsg = df_errmsg['message'].tolist() 
    Errormsg = [s.strip() for s in Errormsg if s != '']
    # print(Errormsg)

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
    # print("list of xpath*****************",xpathlist)
    errorlinks=[]
        

    seismic_l1=[]
    psnow_l1=[]
    hpelearning_l1=[]
    certification_l1=[]
    vshow_l1=[]

    seis_login_link=xpathlist[1][0]
    hpe_learlogin_link=xpathlist[3][0]
    psnow_login_link=xpathlist[5][0]
    vshow_login_link=xpathlist[2][0]


    # Ext_path='External Urls\\External{r}_{c}_{l}_{a}.txt'.format(r=region,c=country,l=language,a=account_type)
    with open('External Urls\ExternalAPJ_Singapore_English_T2.txt','r') as f:
        Ext_path=f.read().splitlines()
    # folder_path = 'External Urls'
    # folder_path += "" if folder_path[-1] == "/" else "/"
    # txt_files = glob.glob(folder_path + "*.txt")

    # # Initialize an empty list to store links
    # Ext_path = []

    # # Read content from each text file
    # for file in txt_files:
    #     with open(file, 'r') as f:
    #         links = f.read().splitlines()
    #         Ext_path.extend(links)
    # print(Ext_path)
    # print("all error links 7777777777777777777",Ext_path)

    for link in Ext_path:     
        if 'seismic' in link:
            seismic_l1.append(link)
        if 'psnow' in link:
            psnow_l1.append(link)
        if 'mylearning'in link:
            hpelearning_l1.append(link)
        if 'certification'in link:
            certification_l1.append(link)
        if 'vshow.' in link:
            vshow_l1.append(link)

    ###########Psnow domain##############
    # print("list of psnhow error links",psnow_l1)
    # psnow_login = EXT_Psnow.check_psnow_login(driver,psnow_login_link,wait,xpathlist,user,password) 
    # for link in psnow_l1:
    #     try:
    #         # Print the link for debugging
    #         print(f"Processing link: {link}")

    #         # Check for errors
    #         Ext_psnow = EXT_Psnow.check_psnow_error(driver, link, Errormsg)
    #         if Ext_psnow:
    #             errorlinks.append(link)
    #     except Exception as e:
    #         # Handle exceptions (e.g., connection errors, timeouts, etc.)
    #         print(f"Error processing link {link}: {str(e)}")
    # print(errorlinks)  

    ############seismic domain############
            
    print("list of Seismic error links",seismic_l1)
    seismic_login = Seismic.check_seismic_login(driver,seis_login_link,wait,xpathlist,user,password)         
    for link in seismic_l1:
        try:
            
            print(f"Processing link: {link}")        
            Ext_seismic = Seismic.check_seismic_error(driver,link,Errormsg)
            if Ext_seismic:
                errorlinks.append(link)
        except Exception as e:        
            print(f"Error processing link {link}: {str(e)}") 
    # print(errorlinks)                           

    ###############hpe_learning domain#############
    # print("list of HPE_learning error links",hpelearning_l1)     
    # hpe_learning_login= EXT_HPELearning.check_learning_login(driver,hpe_learlogin_link,wait,xpathlist,user,password)
    # for link in hpelearning_l1:
    #     try:        
    #         print(f"Processing link: {link}")        
    #         Ext_hpelearning = EXT_HPELearning.check_learning_error(driver,link,Errormsg)
    #         if Ext_hpelearning:
    #             errorlinks.append(link)
    #     except Exception as e:        
    #         print(f"Error processing link {link}: {str(e)}") 
    # print(errorlinks)   
    ###################Certification domain##########################
    # print("list of Certification_learning error links",certification_l1)      
    # hpe_certification_login= EXT_certification.check_certification_losgin(driver,link,wait,xpathlist,user,password)
    # for link in certification_l1:
    #     try:        
    #         print(f"Processing link: {link}")        
    #         Ext_certif = EXT_certification.check_certification_error(driver,link,Errormsg)
    #         if Ext_certif:
    #             errorlinks.append(link)
    #     except Exception as e:        
    #         print(f"Error processing link {link}: {str(e)}") 
    # print(errorlinks)  

    ###########vshow domain##############
    # print("list of vshow error links",vshow_l1)
    # vshow_login=EXT_vshow.check_vs_login(driver,vshow_login_link,wait,xpathlist,user,password)  
    # for link in vshow_l1:
    #     try:        
    #         print(f"Processing link: {link}")        
    #         Ext_vshowval = EXT_vshow.check_vs_error(driver,link,Errormsg)
    #         if Ext_vshowval:
    #             errorlinks.append(link)
    #     except Exception as e:        
    #         print(f"Error processing link {link}: {str(e)}") 
    # print(errorlinks)  
            
   
    df = pd.DataFrame(errorlinks, columns=["Links"])
    # Specify the path where you want to save the Excel file
    excel_file_path = "Externallinks_validated.xlsx"
    # Write the DataFrame to an Excel file
    df.to_excel(excel_file_path, index=False, header=False)
    print(f"Data has been written to {excel_file_path}")              
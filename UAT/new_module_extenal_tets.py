import pandas as pd
import datetime
from os import listdir
from os.path import isfile, join
import os
import ast
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
import External_validation_functions as ext

class PRP():
    xpathlist = []
    Errormsg = []
    excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
    sheetname = 'Error_message'
    delayed_loading_links=work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!=''] 
    absurd_links =work.doc_reader("absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']
    

    def __init__(self, username: str,password: str,region:str,country,language,acc_type):
        self.username=username
        self.password=password
        if region=="NA":
            region='NAR'
        self.region=region
        self.country=country
        self.account_type=acc_type
        self.language=language
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.report_path='Reports\\External_links{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.external_links_path = 'External Urls\\External{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

    def setUp(self):
        webdriver_path = "Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 120, ignored_exceptions=[NoSuchElementException, ElementNotSelectableException, ElementNotVisibleException, StaleElementReferenceException, WebDriverException, TimeoutException])
    
    def read_external_excel(self):
        xpathlist = []
        sheetname = 'Error_message'
        excel_file_path = 'Error messages for external URL\Error messages for external URL.xlsx'
        df_errmsg = pd.read_excel(excel_file_path, sheet_name=sheetname)
        Errormsg = df_errmsg['message'].tolist() 
        Errormsg = [s.strip() for s in Errormsg if s != '']
        # print(Errormsg)

        
        wb = openpyxl.load_workbook(excel_file_path)
        worksheet = wb['URL_credential']
        # print(worksheet,'&&&&&&&&&&&&&&&&&&&&&&&&')
        
        for row in worksheet.iter_rows():   
            row_values = []
            for cell in row:
                row_values.append(cell.value)
            xpathlist.append(row_values)
        wb.close() 
        # print(xpathlist)
        return Errormsg,xpathlist
    
    
    # print("list of xpath*****************",xpathlist)
    def external_url_validation(self):
        driver= self.driver
        wait = self.wait
        errorlinks=[]   
        seismic_l1=[]
        psnow_l1=[]
        hpelearning_l1=[]
        certification_l1=[]
        vshow_l1=[]
        
        Errormsg,xpathlist = self.read_external_excel()

        seis_login_link=xpathlist[1][0]
        hpe_learlogin_link=xpathlist[3][0]
        psnow_login_link=xpathlist[5][0]
        vshow_login_link=xpathlist[2][0]


        with open(self.external_links_path,'r') as f:
            Ext_path=f.read().splitlines()
      
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
        # print("list of psnow error links",psnow_l1)
        # ext.check_psnow_login(self.driver,psnow_login_link,self.wait,xpathlist,self.username,self.password)

        # for link in psnow_l1:
        #     print(f"Processing link: {link}")
        #     Ext_psnow = ext.check_psnow_error(self.driver,link,wait,xpathlist,Errormsg)
        #     if Ext_psnow:
        #         errorlinks.append(link)
        # # print(errorlinks)  

          
        # # # # ###################Certification domain##########################
        # # # # print("list of Certification_learning error links",certification_l1)      
        # ext.check_certification_error(driver,link,Errormsg)
        # for link in certification_l1:                 
        #         print(f"Processing link: {link}")        
        #         Ext_certif = ext.check_certification_error(self.driver,link,Errormsg)
        #         if Ext_certif:
        #             errorlinks.append(link)
        # # #         # # print(errorlinks)              
        # # # # ###########vshow domain##############
        # # # # print("list of vshow error links",vshow_l1)
        # # #ext.check_vs_login(self.driver,vshow_login_link,self.wait,xpathlist,self.username,self.password)  
        # for link in vshow_l1:      
        #         print(f"Processing link: {link}")        
        #         Ext_vshowval = ext.check_vs_error(self.driver,link,Errormsg)
        #         if Ext_vshowval:
        #             errorlinks.append(link)
        # # # # #print(errorlinks)  
        # # self.driver.delete_all_cookies()     
                       
        # #  # ###############hpe_learning domain#############
        # # print("list of HPE_learning error links",hpelearning_l1) 
        # ##ext.check_learning_login(driver,hpe_learlogin_link,wait,xpathlist,self.username,self.password)
        # for link in hpelearning_l1:    
        #         print(f"Processing link: {link}")        
        #         Ext_hpelearning = ext.check_learning_error(self.driver,link,Errormsg)
        #         if Ext_hpelearning:
        #             errorlinks.append(link)
        # # print(errorlinks) 
         ###########seismic domain############                
        print("list of Seismic error links",seismic_l1)
        try:
            ext.check_seismic_login(driver,seis_login_link,wait,xpathlist,self.username,self.password) 
                
            for link in seismic_l1:            
                    print(f"Processing link: {link}")        
                    Ext_seismic = ext.check_seismic_error(self.driver,wait,xpathlist,link,Errormsg)
                    if Ext_seismic:
                        errorlinks.append(link)
        except Exception as e:
             print("error", e)
        # # # print(errorlinks) 
                        
       
        def write_excel(errorlinks):
            file4=open(self.reverse_dict_path)
            a=file4.read()
            dictionary=ast.literal_eval(a)
            issueid = 1
            category = "invalid external links"
            account=self.username
            region=self.region
            country=self.country
            language=self.language
            Fixers =''
            Fixer_mail=''
            status = "New"
            comments = "-"
            report = []
            Domain_map = {'ma'}

            for ele in errorlinks:
                linkele = []
                linkele.append(issueid)
                linkele.append(account)
                linkele.append(category)
                linkele.append(region)
                linkele.append(country)
                linkele.append(language)
                if ele in dictionary:
                        length=len(dictionary[ele])
                        if length> 0:
                            s_url=dictionary[ele][-1]
                            s_url2=dictionary[ele][0]
                elif ele.strip() in dictionary:
                        length=len(dictionary[ele.strip()])
                        if length>0:
                            s_url=dictionary[ele.strip()][-1]
                            s_url2=dictionary[ele.strip()][0]
                else:
                    length=0
                    
                if length==0:
                    req_length=len(str(ele))+1
                    ele=ele.ljust(req_length,'\n')
                    # ele=ele.ljust(req_length,'n')
                    linkele.append(dictionary[ele][-1])
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)
                des ='invalid external links'
                linkele.append(ele)
                linkele.append(des)
                linkele.append(datetime.datetime.now())
                # linkele.append(Fixers)
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid+=1        
                
                r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Mail ID','Status','Comments'])
                r.to_excel(self.report_path)  
        write_excel(errorlinks)   

    def tearDown(self):
        self.driver.close()
        # df=pd.read_excel(self.report_path)
        # if len(df)>0:
        #     work.work_alloc_execute(self.report_path,'Fixers_list.xlsx',self.aruba_links_path)
if __name__=='__main__':
    # credentials = [
    #     ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
    #     ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'],
    #     ['demo_indonesian_id_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'T2'],
    #     ['demo_french_distri@yopmail.com','Login2PRP!','EMEA','France','French','Distri'],
    #     ['demo_french_solp@yopmail.com','Login2PRP!','EMEA','France','French','T2'],
    #     ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'],
    #     ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German','T2'],
    #     ['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
    #     ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
    #     ['demo_turkish_distri@mailinator.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'Distri'],
    #     ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
    #     ['demo_french_distri@yopmail.com','Login2PRP!','EMEA','France','French','Distri'],
    #     ['demo_french_solp@yopmail.com','Login2PRP!','EMEA','France','French','T2'],
    #     ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri'],
    #     ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German','T2'],
    #     ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
    #     ['demo_french_distri@yopmail.com','Login2PRP!','EMEA','France','French','Distri']
    # ]

    credentials = [['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri']]
       
    for acc in credentials:
        print("into new tab\n")
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        print(acc[0])
        Firstrun.setUp()
        Firstrun.external_url_validation()
        Firstrun.tearDown()
        print("going into the next account")    
               
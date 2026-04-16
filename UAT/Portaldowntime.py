import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import win32com.client as win32
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
import time
import urllib3
timeout = urllib3.util.Timeout(connect=2.0, read=1.0)
http=urllib3.PoolManager(timeout=timeout)
from selenium.webdriver.chrome.service import Service
from SelectCertificate import authenticate_with_certificate
 
class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    # delayed_loading_links = work.doc_reader("delayed_loading.docx")
    # delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    # breadcrumb_file=open("UAT\\breadcrumb_links.txt",'r')
    # breadcrumblinks=breadcrumb_file.read().splitlines()
    # breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    breadcrumb_prefix=["https://partner.hpe.com/group/prp/settings-old",'https://partner.hpe.com/group/prp/price-communications']
   
    def __init__(self, username: str,password: str):
        self.username=username
        self.password=password
        self.broken_links=[]
      
    def setUp(self):
        webdriver_path="Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver=webdriver.Chrome(service=service)
        self.driver.maximize_window() 
 
    def test_load_home_page(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        print("*&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
        print("***********")
        try:
            authenticate_with_certificate('BOT DEC-D001a') # select certificate
        except:
            print('\nNO CERTIFICATE SELECTION\n')
            pass
        time.sleep(5) 

        
 
    def email(self):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        # mail.To = 'prpalerts@hpe.com'  
        mail.To = 'darshini.k-v@hpe.com;biki.dey@hpe.com;pranav-m.bhat@hpe.com;rohitashwyo.dutta-chowdhury@hpe.com;mrunal.vinod@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;srividya-d@hpe.com;weiwei.shao@hpe.com;kalaivanan.a@hpe.com;probles@hpe.com;taoy@hpe.com'
        mail.Subject = 'Partner Ready Portal is down for Partners'
        mail.Body ='''Hi there! 
The Partner Ready Portal is inaccessible to partners. 
Please take necessary action as earliest.
Thank you, 
Albert salutes you.'''
        mail.Send() 
    
    def check_portal_health(self,link):
        # self.email()
        try:
            r=http.request("GET",link)
        except Exception as e:
            ee=str(e)
            if "NewConnectionError" in ee or "MaxRetryError" in ee :
                time.sleep(15)
                try:
                    r=http.request("GET",link)
                except Exception as e:
                    ee=str(e)
                    if "NewConnectionError" in ee or "MaxRetryError" in ee :
                        self.email()
                        print('portal down')
                        time.sleep(1800)
                
                   
                
                

        #         self.broken_links.append(link)
        # errors = [
        #     "NOT FOUND The requested resource could not be found",
        #     "Service Unavailable The server is temporarily unable to service your request. Please try again later",
        #     "Service Unavailable The server is temporarily unable to service your request due to maintenance downtime capacity",
        #     "This site can’t be reached cf-passport.it.hpe.com's server IP address could not be found",
        #     "400 Bad Request",
        #     "HTTP status 403 Request forbidden. Transaction ID: XXXXXXXXXXXXXXXXXXXXXX failed",
        #     "Service Unavailable DNS failure The server is temporarily unable to service your request. Please try again later"
        # ]
        # self.driver.get(link)
        # pgsrc = self.driver.page_source
        # # print(pgsrc,'*********')
        # for errmsg in errors:
        #     if errmsg in pgsrc:
        #         return errmsg            
           
    def health(self):
        link1="https://partner.hpee.com/group/prp/home"
        link1 = 'partnerrrrr.com'
        while True:
            self.check_portal_health(link1)
            # self.email(error)
           
         
    def tearDown(self):
        self.driver.close() 

credentials=[
    # ['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
             ['bot.dec-d001a@hpe.com','Login2PRP!']]
 
for acc in credentials:
    start_time=time.time() 
    Firstrun=PRP(acc[0],acc[1])
    Firstrun.setUp()
    # Firstrun.test_load_home_page()
    # time.sleep(10)
    Firstrun.health()
    Firstrun.tearDown()
    print("going into the next account")
    end_time=time.time()
    run_time=end_time-start_time
    print("Runtime_demoacc_name:",run_time,"second")
     
'''lst =[sign-in]'''    
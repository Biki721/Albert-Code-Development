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
 
class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    f = open('UAT\delayed_loading.txt',"r+")
    delayed_loading_links = f.read().splitlines()
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    breadcrumb_file=open("UAT\\breadcrumb_links.txt",'r')
    breadcrumblinks=breadcrumb_file.read().splitlines()
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    breadcrumb_prefix=["https://partner.hpe.com/group/prp/settings-old",'https://partner.hpe.com/group/prp/price-communications']
   
    def __init__(self, username: str,password: str):
        self.username=username
        self.password=password
     
 
 
   
    def setUp(self):
        self.driver=webdriver.Chrome(executable_path=self.webdriver_path)
        self.driver.maximize_window()
         
       
 
    def test_load_home_page(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div/div[2]/form/div[3]/button"))).click()  
        time.sleep(20)    
 
    def email(self, errmsg):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = 'pranav-m.bhat@hpe.com'  
        mail.Subject = errmsg[0]
        mail.Body = errmsg[1]
        mail.Send()
 
    broken_links=[]
    def check_portal_health(self,link):
        try:
            r=http.request("GET",link)
        except Exception as e:
            ee=str(e)
            if "NewConnectionError" in ee or "MaxRetryError" in ee :
            #print('broken link', link)
                broken_links.append(link)
        errors = [
            "NOT FOUND The requested resource could not be found",
            "Service Unavailable The server is temporarily unable to service your request. Please try again later",
            "Service Unavailable The server is temporarily unable to service your request due to maintenance downtime capacity",
            "This site can’t be reached cf-passport.it.hpe.com's server IP address could not be found",
            "400 Bad Request",
            "HTTP status 403 Request forbidden. Transaction ID: XXXXXXXXXXXXXXXXXXXXXX failed",
            "Service Unavailable DNS failure The server is temporarily unable to service your request. Please try again later"
        ]
        self.driver.get(link)
        pgsrc = self.driver.page_source
        for errmsg in errors:
            if errmsg in pgsrc:
                return errmsg             
           
    def health(self):
        link1=["https://partner.hpe.com/web/prp/login/login","https://partner.hpe.com/group/prp/home"]
        for link in link1:
            error=self.check_portal_health(link)
        self.email(error)
           
             
    def tearDown(self):
                self.driver.close()
 
 
 
 
credentials=[['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
 
for acc in credentials:
    Firstrun=PRP(acc[0],acc[1])
    Firstrun.setUp()
    Firstrun.check_portal_health()
    Firstrun.tearDown()
    print("going into the next account")
     
'''lst =[sign-in]'''    
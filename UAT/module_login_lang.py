# THIS MODULE LOGS INTO THE SETTINGS PAGE AND DETECTS THE DISPLAY LANGUAGE. IF THE DISPLAY LANGUAGE IS NOT THE LOCAL LANGUAGE, THE LOCAL LANGUAGE IS CHOSEN

from ast import main
from sys import exception
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, TimeoutException,ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from SelectCertificate import authenticate_with_certificate
# from SelectCertificate_phase_3 import authenticate_with_certificate_win32 as authenticate_with_certificate
import VaultSample
from demo_attribute_check import login
import work_phase_3 as work
import ast
import win32com.client as win32
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
import datetime
import threading
import pyautogui
import pygetwindow as gw
from merge_upload import generate_session_id
from metric_report import metric_report
from pynput.keyboard import Key, Controller
from concurrent.futures import ThreadPoolExecutor

class PRP():
    base_url='https://partner.hpe.com/group/prp/settings'
    # base_url = 'https://partner.hpe.com/group/prp/distributor-zone'
    # f= open('delayed_loading.txt',"r+")
    delayed_loading_links =work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    # breadcrumb_file=open("breadcrumb_links.txt",'r')
    breadcrumblinks=work.doc_reader("breadcrumb_links.docx")
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    absurd_links =work.doc_reader("absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']
    # print(absurd_links)
    breadcrumb_prefix=work.doc_reader("Breadcrumb_Prefix.docx")
    breadcrumb_prefix=[s.strip() for s in breadcrumb_prefix if s!='']
    # breadcrumb_prefix=[https://partner.hpe.com/group/prp/settings-old,'https://partner.hpe.com/group/prp/price-communications','https://partner.hpe.com/group/prp/reports']

    def __init__(self, username: str,password: str,region:str,country,language,acc_type):
        self.username=username
        self.password=password
        if region=="NA":
            region='NAR'
        self.region=region
        self.country=country
        self.account_type=acc_type
        self.language=language

        if language=='Taiwan':
            self.language = 'Chinese'
        elif language=='LARSpanish':
            self.language='Spanish'

        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        #self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.doc_link_path ='DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.external_urls_path='External Urls\\External{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

        self.login_errmsg = ['Albert demo account login error',\
            'Hi there!\n\nThe demo account '+self.username+' has a login error.\nPlease check & fix the issue at the earliest.\n\nThank you,\nAlbert salutes you.']
        self.lang_errmsg = ['Demo account preferred language issue - Fixed',\
            'Hi there!\n\nAlbert noticed the error in the preferred language for '+self.username+' and changed it to the local language.\n\nThank you,\nAlbert salutes you.']
        self.lang = {'en-US':'English', 'fr-FR':'French', 'de-DE':'German', 'it-IT':'Italian', 'ja-JA':'Japanese', 'ko-KO':'Korean', \
            'pt-PT':'Portuguese', 'pt-BR':'Portuguese', 'ru-RU':'Russian', 'es-ES':'Spanish', 'zh-TW':'Chinese', \
            'zh-CN':'Chinese', 'tr-TR':'Turkish', 'id-ID':'Indonesian'}
        
        self.session_id = generate_session_id(self.language)

        self.current_datetime = datetime.datetime.now()

        
        self.current_date = None
        self.current_month = None
        self.current_time = None
        
    
    def setUp(self):
        # webdriver_path = "Webdrivers\\chromedriver.exe"
        # service = Service(webdriver_path)
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) 
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()  
        time.sleep(10)
        self.wait = WebDriverWait(self.driver,10,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])


    def email(self, errmsg):
        # print('Sending mail')
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        # mail.To = 'biki.dey@hpe.com;pranav-m.bhat@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;srividya-d@hpe.com;ragul.subramani@hpe.com;marina.melcioiu@hpe.com;kalaivanan.a@hpe.com;peng.wang3@hpe.com;probles@hpe.com;weiwei.shao@hpe.com;xiaojie.feng@hpe.com;salazar-guevara@hpe.com'
        mail.To = 'biki.dey@hpe.com'
        # mail.To = 'biki.dey@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;weiwei.shao@hpe.com'
        mail.Subject = errmsg[0]
        mail.Body = errmsg[1]
        mail.Send() 
        return 


    def test_load_home_page(self):
    
        global login_title, driver
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        login_title = self.driver.title
        # print('login_title : ',login_title)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
        time.sleep(20)
        elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form19"]/div[2]/div[2]/div[2]/a')))
        elem.click()
        time.sleep(20) 
    
    def tearDown(self):
        driver.close()

    def login(self):
        global login_title
        self.test_load_home_page()
       
        try:
            time.sleep(5)
            self.wait.until(EC.title_contains('Settings'))
        except:
            print('\nTIMEOUT EXCEPTION-------->SETTINGS PAGE FAILED TO LOAD')

        new_title = self.driver.title

        if login_title==new_title:
            print('DEMO ACCOUNT',self.username,'FAILED TO LOGIN')
            self.driver.close()
            try:
                self.email(self.login_errmsg)
            except exception as e:
                print(e)
            return False
        

        def detect_lang(self):
            # self.driver.get('https://partner.hpe.com/group/prp/settings')
            page = self.driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            disp_lang = soup.html.get('lang')
            disp_lang = self.lang.get(disp_lang)
            print('DISPLAY LANGUAGE:',disp_lang,'\nPREF LANGUAGE:',self.language)
            return disp_lang
        


        def change_lang(self):
            try:
                input_lang = self.wait.until(EC.presence_of_element_located((By.ID, '_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_INSTANCE_WIWF7MxPXFUm_preferredLanguage')))
                input_lang.click()
                input_lang = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[text()='" + self.language + "']"))).click()
                save_button = self.driver.find_element(By.ID, "personal-save-personal-cancel")
                self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
                time.sleep(10)
                self.wait.until(EC.element_to_be_clickable((By.ID, "personal-save-personal-cancel"))).click()
                try:
                    self.email(self.lang_errmsg)
                except exception as e:
                    print(e)

                time.sleep(10)
                self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-toolbar-button btn btn-default yui3-widget aui-button yui3-aui-button yui3-aui-button-content cancelButton tertiaryButton btn-default btn cancelButton tertiaryButton btn-default btn-content yui3-aui-button-focused"))).click()
                

            except TimeoutException:
                print('COULD NOT FIND BUTTON')

        self.disp_lang = detect_lang(self)
        
        self.current_date = self.current_datetime.date()
        self.current_month = self.current_date.strftime("%B")
        self.current_time = self.current_datetime.strftime("%H:%M:%S")
        if self.disp_lang != self.language:
            change_lang(self)
            metric_report('Language',self.session_id,self.username,str(self.current_month),str(self.current_date),str(self.current_time),'Yes')
        
        else:
            metric_report('Language',self.session_id,self.username,str(self.current_month),str(self.current_date),str(self.current_time),'No')



        self.driver.close()
        #print('driver closed/0000000000000000000000000000000')

        return True
    

def run_account(account):
    try:
        # print("Into broken link module\n")
        # print(account[0])
        prp = PRP(*account)
        prp.setUp()
        prp.login()
        prp.tearDown()
        from playsound3 import playsound
        playsound("C:/Users/deyb/Downloads/beep-01a.wav")
        print("Finished processing:", account[0])
    except Exception as e:
        print(f"Error while processing {account[0]}: {e}")
      
    

           
    
    

if __name__=='__main__':
    credentials = [
        # ['demo_french_distri@yopmail.com','Want2seePRP!','EMEA','France','French','Distri'],
        # ['demo_emea_platinum@pproap.com', 'Want2seePRP!', 'EMEA', 'Germany', 'German','T2'],
        # ['demo_italian_distri@yopmail.com', 'Want2seePRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
        # ['demo_turkish_solp@yopmail.com', 'Want2seePRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
        # ['demo_ukeng_distri@yopmail.com', 'Want2seePRP!', 'EMEA', 'UK', 'English', 'Distri'],
        # ['demo_la_platinum@pproap.com', 'Want2seePRP!', 'NAR', 'MEXICO', 'Spanish', 'T2'],
        ['demo_h3c@pproap.com', 'Want2seePRP!', 'APJ', 'China', 'Chinese', 'T2'],
        ['demo_na_distributor@pproap.com', 'Want2seePRP!', 'NAR', 'USA', 'English', 'Distri'],
        ['demo_traditional_cn_distributor@pproap.com','Want2seePRP!','APJ','Taiwan','Taiwai','Distri'],
        ['demo_indonesian_distributor@pproap.com', 'Want2seePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'],
        ['demo_japanese_distributor@pproap.com','Want2seePRP!','APJ','Japan','Japanese','Distri'],
        ['demo_korean_kr_t2solutionprovider@pproap.com', 'Want2seePRP!', 'APJ', 'Korea', 'Korean', 'T2']
    ]
    # Adjust max_workers based on your system capability (e.g., RAM, CPU, browser limits)
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(run_account, credentials)
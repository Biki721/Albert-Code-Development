from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import requests
import time
import pandas as pd
import datetime
from SelectCertificate import authenticate_with_certificate
import work
import VaultSample
from selenium.webdriver.chrome.service import Service


class PRP():
    base_url="https://partner.hpe.com"
    
    webdriver_path="Webdrivers\\chromedriver.exe"
    # f= open('delayed_loading.txt',"r+")
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
        self.report_path='Reports\\New_Tab_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

    def setUp(self):
        webdriver_path = 'Webdrivers\\chromedriver.exe'
        service = Service(webdriver_path)
        self.driver=webdriver.Chrome(service=service)
        self.driver.maximize_window() 
        self.wait = WebDriverWait(self.driver,10,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])

    def test_load_home_page(self):

        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
        try:
            authenticate_with_certificate('BOT DEC-D001a') # select certificate
        except:
            print('\nNO CERTIFICATE SELECTION\n')
            pass
        time.sleep(5)
        # time.sleep(5)
        # print("going to certi")
        # try:
        #     SelectCertificate.authenticate_with_certificate('')
        #     SelectCertificate.handle_pin_prompt('')
        # except:
        #     pass
        # time.sleep(15)

    def test_new_tab(self): 
        self.test_load_home_page()
        # allurls=set()
        notopening = []
        # opening = []
        def demo_test(site,driver):
            try:
                driver.get(site)
                if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links or site in self.absurd_links:
                    time.sleep(30)
            except:
                #print("not opening",site)
                pass
            else:
                if 'notification' in site:
                    return
                all_links = []
                try:
                    res = driver.find_elements(By.TAG_NAME,"a")
                    for link in res:
                        all_links.append([link.get_attribute("href"), link.get_attribute('target')])
                except:
                    pass
                    #print("Encounted Error")
                # print(len(checks),site)
                for i in range(len(all_links)):
                    # print(link)
                    # if link not in allurls:
                        attr = all_links[i][1]
                        # print(attr,link)
                        # if all_links[i][0] is not None and all_links[i][0].startswith("https://partner.hpe.com/") and 'logout' not in all_links[i][0]:
                        #     if attr == "_blank" and '/esm/' not in link:
                        #         # print('Error opening',site,link)
                        #         opening.append([site,link])

                        if all_links[i][0] is not None and all_links[i][0].startswith("http") and 'partner' not in all_links[i][0]:
                            if attr != "_blank" and attr!='blank' and attr!='new' and attr!='_new':
                                # print(attr,link)
                                # print('Error not opening',site,link)
                                notopening.append([site,all_links[i][0]])
                    # allurls.add(link)
                                
        def write_excel():
            issueid = 1
            category = "New Tab"
            account=self.username
            region=self.region
            country=self.country
            language=self.language
            Fixers =''
            Fixer_mail=''
            status = "New"
            comments = "-"
            report = []

            for ele in notopening:
                linkele = []
                linkele.append(issueid)
                linkele.append(account)
                linkele.append(category)
                linkele.append(region)
                linkele.append(country)
                linkele.append(language)
                des ='Link not opening in a new tab'
                linkele.append(ele[0])
                linkele.append(ele[1])
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
        

            # r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Fixers','Mail ID','Status','Comments'])
            # r.to_excel(self.report_path)
        file1 = open(self.page_tree_path, 'r')
        Lines = file1.readlines()
        for line in Lines:
            demo_test(line,self.driver)
        write_excel()
           
    def tearDown(self):
        self.driver.close()
        df=pd.read_excel(self.report_path)
        if len(df)>0:
            work.work_alloc_execute(self.report_path,'Fixers_list.xlsx',self.aruba_links_path)

#credentials=VaultSample.result    
# credentials=[["demo_na_platinum@pproap.com","Login2PRP!","NAR",'USA',"English","Distri"]]  
# credentials=[["mapdummypartner@yopmail.com","Login2PRP!","EMEA",'Croatia',"English","MAP"]]
# credentials=[["demo_na_distributor@pproap.com","Login2PRP!",'NAR','USA','English','Distri'],
# ["mapdummypartner@yopmail.com","Login2PRP!","EMEA",'Croatia',"English","MAP"],
# ["demo_emea_platinum@pproap.com","Login2PRP!","EMEA",'USA','English','T2'],
# ['demo_hreng_mapt2@yopmail.com','Login2PRP!','EMEA','Croatia','English','T2'],
# ['demo_mapcompetitor_solp@yopmail.com','Login2PRP!','EMEA','Lithuania','English','T2']]
# credentials=[['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'], ['demo_japanese_jp_competitor@pproap.com', 'Login2PRP!', 'APJ',
# 'Japan', 'Japanese', 'T2A'], ['demo_japanese_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'Distri']]
#credentials=[#['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri'],
# ['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
# ['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2']
# credentials=[#['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# # ['demo_turkish_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
# # ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2A'],['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# # ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],#['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri']]
# # ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# # ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]

if __name__=='__main__':
    credentials = [
        ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
        # ['demo_hpelarptbr_01@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']
    ]
    for acc in credentials:
        print("into new tab\n")
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        print(acc[0])
        Firstrun.setUp()
        Firstrun.test_new_tab()
        Firstrun.tearDown()
        print("going into the next account")
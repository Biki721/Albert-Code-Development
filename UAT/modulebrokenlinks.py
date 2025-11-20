import time
import pandas as pd
import datetime
import work
import VaultSample
import urllib3
import json
timeout = urllib3.util.Timeout(connect=2.0, read=1.0)
http=urllib3.PoolManager(timeout=timeout)
import ast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from SelectCertificate import authenticate_with_certificate
from selenium.webdriver.chrome.service import Service

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"

    # f=open("lte_external.txt")
    # links_to_exclude=f.read().splitlines()
    # links_to_exclude=[s.strip() for s in links_to_exclude if s!='']
    # print(links_to_exclude)

    links_to_exclude=work.doc_reader("lte_external.docx")
    links_to_exclude=[s.strip() for s in links_to_exclude if s!='']
    # print(links_to_exclude)
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
        self.report_path='Reports\\Broken_Link_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.external_urls_path='External Urls\\External{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.document_links='DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

    def setUp(self):
        webdriver_path = 'Webdrivers\\chromedriver.exe'
        service = Service(webdriver_path)
        self.driver=webdriver.Chrome(service=service)
        self.driver.maximize_window()

    def test_load_home_page(self):
        wait = WebDriverWait(self.driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        self.driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()


    def test_multiple_broken(self):   
        
        def brokencheck():
            broken_links = []
            l1 = open(self.page_tree_path, 'r').read().splitlines()
            l2 = open(self.external_urls_path,'r').read().splitlines()
            l3 = open(self.document_links,'r').read().splitlines()

            #***** UNCOMMENT LATER******
            l4=l1+l2+l3
            all_links_to_be_checked=[link.strip() for link in l4 if (link.strip() not in self.links_to_exclude and link!='')]
            #print(all_links_to_be_checked)
            for link in all_links_to_be_checked:
                link=link.rstrip()
                #print (link)
                try:
        
                    r=http.request("GET",link)
                except Exception as e:
                    ee=str(e)
                    if "NewConnectionError" in ee or "MaxRetryError" in ee :
                        #print('broken link', link)
                        broken_links.append(link)

                ########################## EVALUATE BROKEN LINKS THAT HAVE NO REQUEST EXCEPTION ########################
                # self.driver.get(link)
                # pgsrc = self.driver.page_source
                # errmsg = ['Oops! We can’t find that page', 'We can’t find the page you’re looking for', 'Page not found']
                # for i in errmsg:
                #     if pgsrc and i in pgsrc:
                #         print('BROKEN LINK!!!\n')
                #         broken_links.append(link)
                        
            #*******************************************
            #print("onto externals")

            # for link in file2.readlines():
            #     if link not in self.links_to_exclude:
            #     #print(link)
            #         link=link.rstrip()
            #         try:
            
            #             r=http.request("GET",link)
                    
            #         except Exception as e:
        
            #             ee=str(e)
            #             if "NewConnectionError" in ee or "MaxRetryError" in ee:
            #                 #print('broken link', link)
            #                 broken_links.append(link)
                
           
                    
            # #print("onto doc links")
            # #UNCOMMENT LATER ********************
            # for link in file3.readlines():
            #     #print(link)
            #     link=link.rstrip()
            #     try:
        
            #         r=http.request("GET",link)
                
            #     except Exception as e:
      
            #         ee=str(e)
            #         if "NewConnectionError" in ee or "MaxRetryError" in ee:
            #             print('broken link', link)
            #             broken_links.append(link)
            
            # #********************
            
            
            #print("Time taken:",tottime)
            write_excel(broken_links)
            return

        def write_excel(broken_links):
            file4=open(self.reverse_dict_path)
            a=file4.read()
            dictionary=ast.literal_eval(a)
            issueid = 1
            category = "Broken Link"
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

            for ele in broken_links:
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
                des ='Broken link'
                linkele.append(ele)
                linkele.append(des)
                linkele.append(datetime.datetime.now())
                # linkele.append(Fixers)
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid+=1

            #print(broken_links)

            r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Mail ID','Status','Comments'])
            r.to_excel(self.report_path)
        brokencheck() 
        
           
    def tearDown(self):
        self.driver.close()
     
        df=pd.read_excel(self.report_path)
        if len(df)>0:
            work.work_alloc_execute(self.report_path,'Fixers_list.xlsx',self.aruba_links_path)

# credentials = [['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2A']]

# credentials = [['demo_mapcompetitor_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Lithuania ', 'English', 'T2']]
#credentials=[['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri']] 
# credentials=[["mapdummypartner@yopmail.com","Login2PRP!","EMEA",'Croatia',"English","MAP"]]
# credentials=[["demo_na_distributor@pproap.com","Login2PRP!",'NAR','USA','English','Distri']]
# ["mapdummypartner@yopmail.com","Login2PRP!","EMEA",'Croatia',"English","MAP"],
# credentials=[["demo_russian_solp@yopmail.com","Login2PRP!","EMEA",'Russia','Russian','T2']]
# ['demo_hreng_mapt2@yopmail.com','Login2PRP!','EMEA','Croatia','English','T2'],
# ['demo_mapcompetitor_solp@yopmail.com','Login2PRP!','EMEA','Lithuania','English','T2']]
# credentials=[["demo_na_platinum@pproap.com","Login2PRP!","NAR",'USA',"English","Distri"]]
# credentials=VaultSample.result
# print(credentials)
# credentials=[['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'], ['demo_japanese_jp_competitor@pproap.com', 'Login2PRP!', 'APJ',
# 'Japan', 'Japanese', 'T2A'], ['demo_japanese_distributor@pproap.com', 
# credentials=[['Login2PRP!', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'Distri']]

# credentials=[#['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri']]
# # ['demo_turkish_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
# # ['demo_ukeng_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'T2A'],['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# # ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# #['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]#['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# # ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# # ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# #['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]

if __name__=='__main__':
    credentials=[#['demo_french_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'Distri'],
    # ['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
    # ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
    # ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
    # ['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
    # ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
    ['demo_emea_distributor@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'Distri']]
    for acc in credentials:
        print("into broken link module\n")
        print(acc[0])
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        Firstrun.setUp()
        Firstrun.test_load_home_page()
        Firstrun.test_multiple_broken()
        Firstrun.tearDown()
        print("going into the next account")
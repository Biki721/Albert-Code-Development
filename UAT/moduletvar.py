from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException,InvalidArgumentException
from selenium.webdriver.common.by import By
import datetime
import re
import pandas as pd
import work
import SelectCertificate
import VaultSample
import ast

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    def __init__(self, username: str,password: str,region:str,country,language,acc_type):
        self.username=username
        self.password=password
        if (region=="NA"):
            region = "NAR"
        self.region=region
        self.country=country
        self.account_type=acc_type
        self.language=language
        self.document_links='DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,a=self.account_type,l=self.language,c=self.country)
        self.report_path='Reports\\Tvar_Check_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,a=self.account_type,l=self.language,c=self.country)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        
    

    def test_tvar_check(self): 
        
        def tvar_check(link):
          
            #doc_types=['.pdf','.xlsx','.doc','.docx','.odt','.txt','.exe','.docm','.xml','.zip','.tar.gz']
    
            if re.search(r'\?t=',link): 
                    return link
            return ''
        def call_tvar_check():
            f = open(self.document_links)
            all_links=list(f.readlines())
            output=[]
            for i in range(len(all_links)):
                match = tvar_check(all_links[i])
                if (match):
                    output.append(match)
            
            write_excel(output)

            return
        def write_excel(errors):
            f = open(self.reverse_dict_path)
            dictstr = f.read()
            mega_dict=ast.literal_eval(dictstr)

            linkele = []
            for ele in errors:
                #print(ele)
                if ele in mega_dict:
                            length=len(mega_dict[ele])
                            if length> 0:
                                s_url=mega_dict[ele][-1]
                                s_url2=mega_dict[ele][0]
                elif ele.strip() in mega_dict:
                            length=len(mega_dict[ele.strip()])
                            if length>0:
                                s_url=mega_dict[ele.strip()][-1]
                                s_url2=mega_dict[ele.strip()][0]
                else:
                    length=0
                    
                if length==0:
                    req_length=len(str(ele))+1
                    ele=ele.ljust(req_length,'\n')
                    # ele=ele.ljust(req_length,'n')
                    linkele.append(mega_dict[ele][-1])
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)
            account=self.username
            region = self.region
            country=self.country
            language=self.language
            issueid = [i+1 for i in range(len(errors))]
            category = ["?t variable"]*len(errors)
            status = ["New"]*len(errors)
            comments = ["-"]*len(errors)
            description = ["Tvar"]*len(errors)
            time = [datetime.datetime.now()]*len(errors)
            result = {'Issue ID':issueid,'Demo Account': account,'Category':category,'Link':linkele,'Error Link':errors,'Description':description,'Time Identified':time,'Region':region,'Country':country,'Language':language,'Mail ID':"none",'Status':status,'Comments':comments}
            df = pd.DataFrame.from_dict(result)
            df.to_excel(self.report_path)
            return
        
        #self.test_load_home_page()
        call_tvar_check()
                
        
    def tearDown(self):
        #self.driver.close()
        df=pd.read_excel(self.report_path)
        if len(df)>0:
            work.work_alloc_execute(self.report_path,'Fixers_list.xlsx',self.aruba_links_path)

credentials=[['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2']]
# credentials=[["demo_na_distributor@pproap.com","ExperiencePRP!",'NAR','USA','English','Distri'],
# ["mapdummypartner@yopmail.com","ExperiencePRP!","EMEA",'Croatia',"English","MAP"],
# ["demo_emea_platinum@pproap.com","ExperiencePRP!","EMEA",'USA','English','T2'],
# ['demo_hreng_mapt2@yopmail.com','ExperiencePRP!','EMEA','Croatia','English','T2'],
# ['demo_mapcompetitor_solp@yopmail.com','ExperiencePRP!','EMEA','Lithuania','English','T2']]
# credentials=VaultSample.result
# credentials=[['demo_french_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'France', 'French', 'T2'],
# ['demo_la_distributor@pproap.com', 'ExperiencePRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],
# ['demo_spanisheu_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'],
# ['demo_na_proximity@pproap.com', 'ExperiencePRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# ['demo_turkish_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
# ['demo_ukeng_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'UK', 'English', 'T2A']]
for acc in credentials:
    print("Tvar module")
    Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
    #Firstrun.setUp()
    Firstrun.test_tvar_check()
    Firstrun.tearDown()
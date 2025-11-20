import work
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import ast
import datetime
from selenium import webdriver
import moduletranslation as mtrans
from bs4 import BeautifulSoup
import pandas as pd
import moduleemptypage as mep
import time
import docx
from selenium.webdriver.chrome.service import Service
import module_login_lang

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    
    links_not_to_be_checked=work.doc_reader("lte_translation.docx")
    breadcrumblinks=[s.strip() for s in links_not_to_be_checked if s!='']
    # links_not_to_be_checked = f.read().splitlines()
    # links_not_to_be_checked = [s.strip() for s in links_not_to_be_checked if s!='']
    # f.close()
    translated_phrases={"French":"Contenu associé",'German':'Verwandter inhalt','Italian':"Contenuti correlati",'Chinese':'相关内容','Russian':'Сопутствующая информация','Portugese':'Conteúdo relacionado','Indonesian':'Konten terkait','Singaporean':'Related content','Korean':"관련 콘텐츠",'Turkish':"İlgili içerik",'Japanese':"関連コンテンツ",'Taiwan':"相關內容",'Spanish':'Contenido relacionado',"LARSpanish":'Contenido relacionado','English':'Related content'}
    # f= open('delayed_loading.txt',"r+")
    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!=''] 
    # f = open('lte_emptypage.txt','r+')
    not_to_check_links=work.doc_reader("lte_emptypage.docx")
    not_to_check_links=[s.strip() for s in not_to_check_links if s!='']
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
        # self.langcode=self.codes[self.language]
        # self.langtransterm=self.trans_terms[self.language]
        self.page_tree_path='Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.all_links_path='All Links\\AllLinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.translation_report_path='Reports\\Translation_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.emptypage_report_path='Reports\\EmptyPage_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.phrase=self.translated_phrases[language]
        self.defaultphrase="Related content"
        self.reverse_dict_path='Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

    def setUp(self):
        webdriver_path = "Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window() 

    def test_load_home_page(self): 
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click() 
    
    def parent(self):
        def write_excel(errors):
            # print("writing to excel")
            fileread=open(self.reverse_dict_path).read()
            dictionary=ast.literal_eval(fileread)
            if type(errors)==dict:
                category = 'Translation Error'
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
                published_report_path=self.translation_report_path
            else:
                category = 'Empty Page'
                iterator = errors
                des =['Empty page']*len(errors)
                published_report_path=self.emptypage_report_path
               
            issueid = 1
    
            account=self.username
            region=self.region
            country=self.country
            language=self.language
            Fixers =''
            Fixer_mail=''
            status = "New"
            comments = "-"
            report = []
            i = 0
            for ele in iterator:
                # print("in iterator")
                if ele=="https://partner.hpe.com/group/prp/internal":
                    continue
                # ele=ele.strip()
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
                elif ele+"\n" in dictionary:
                    length = len(dictionary[ele+"\n"])
                    if length>0:
                            s_url=dictionary[ele+"\n"][-1]
                            s_url2=dictionary[ele+"\n"][0]
                else:
                    length=0
                    
                if length==0:
                    linkele.append(ele)
                elif s_url==ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)

                linkele.append(ele)
                #linkele.append(errors[ele])
                linkele.append(des[i])
                linkele.append(datetime.datetime.now())
                # linkele.append(Fixers)
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid+=1
                i+=1
            
            # print(published_report_path)
            r = pd.DataFrame(report,columns=['Issue ID','Demo Account','Category','Region','Country','Language','Link','Error Link','Description','Time Identified','Mail ID','Status','Comments'])
            r.to_excel(published_report_path)
            return

        def integrate(site):
            self.driver.get(site)
            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links or site in self.absurd_links:
                time.sleep(30)
            src = self.driver.page_source
            soup=BeautifulSoup(src,'html.parser')
            return src,soup


        def filter(list_of_links,links_not_to_be_checked):
                actual_list_of_links=[]
                list_of_links = [link.strip() for link in list_of_links]
                links_not_to_be_checked = [link.strip() for link in links_not_to_be_checked]
                actual_excluded_links = set()
                for lte in links_not_to_be_checked:
                    for ptl in list_of_links:
                        if ptl.startswith(lte) or "products" in ptl:
                            actual_excluded_links.add(ptl)
                actual_list_of_links = list(set(list_of_links)-set(actual_excluded_links))
                actual_list_of_links.insert(0,'https://partner.hpe.com/group/prp/internal') 
                return actual_list_of_links

        f=open(self.page_tree_path,'r')
        list_of_links=f.read().splitlines()
        #print(list_of_links)
        #pass links not to be checked paths here
        all_links_trans = filter(list_of_links,self.links_not_to_be_checked)
        # print("to runtrans",all_links_trans)
        all_links_empty = filter(list_of_links,self.not_to_check_links)
        # print("to runempty",all_links_empty)
        #print(all_links_empty,all_links_trans)
        errors = {}
        epterrors=[]
        for link in list_of_links:
            if link in all_links_trans and link in all_links_empty:
                src,soup = integrate(link)
                #print(self.language)
                if self.language!='English' and self.language!='Singaporean':
                    #print("inside first if")
                    err = mtrans.callable_extract(link,src,soup,self.language)
                    if err:
                        errors.update({link:err})
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))
            elif link in all_links_empty:
                src,soup = integrate(link)
                epterrors.append(mep.emptypagecheck(link,self.phrase,self.defaultphrase,soup))
            elif link in all_links_trans:
                src,soup = integrate(link)
                if self.language!='English' and self.language!='Singaporean':
                    #print("second if")
                    err = mtrans.callable_extract(link,src,soup,self.language)
                    if err:
                        errors.update({link:err})
            else:
                continue
        epterrors = [err for err in epterrors if err!='']
        # print(epterrors)
        write_excel(epterrors)
        # print(errors,type(errors))
        write_excel(errors)
        
    def tearDown(self):
        self.driver.close()
        df=pd.read_excel(self.translation_report_path)
        dff=pd.read_excel(self.emptypage_report_path)
        if len(df)>0:
            work.work_alloc_execute(self.translation_report_path,'Fixers_list.xlsx')
        if len(dff)>0:
            work.work_alloc_execute(self.emptypage_report_path,'Fixers_list.xlsx')

credentials = [['demo_french_distri@yopmail.com','Login2PRP!','EMEA','France','French','Distri']]
for acc in credentials:
        # Firstrun = module_login_lang.PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5]) 
        # Firstrun.setUp()
        # login_bool = Firstrun.login()
        # if login_bool is False:
        #     print('DEMO ACCOUNT',acc,'FAILED TO LOGIN')
        # time.sleep(10)
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        Firstrun.setUp()
        Firstrun.test_load_home_page()
    
        Firstrun.parent()
        Firstrun.tearDown()

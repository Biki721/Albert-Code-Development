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

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    
    f = open('lte_translation.txt','r+')
    links_not_to_be_checked = f.read().splitlines()
    links_not_to_be_checked = [s.strip() for s in links_not_to_be_checked if s!='']
    f.close()
    translated_phrases={"French":"Contenu associé",'German':'Verwandter inhalt','Italian':"Contenuti correlati",'Chinese':'相关内容','Russian':'Сопутствующая информация','Portugese':'Conteúdo relacionado','Indonesian':'Konten terkait','Singaporean':'Related content','Korean':"관련 콘텐츠",'Turkish':"İlgili içerik",'Japanese':"関連コンテンツ",'Taiwan':"相關內容",'Spanish':'Contenido relacionado',"LARSpanish":'Contenido relacionado','English':'Related content'}
    f= open('delayed_loading.txt',"r+")
    delayed_loading_links = f.read().splitlines()
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!=''] 
    f = open('lte_emptypage.txt','r+')
    not_to_check_links=f.read().splitlines()
    not_to_check_links=[s.strip() for s in not_to_check_links if s!='']

 
    
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
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)


    def setUp(self):
        self.driver=webdriver.Chrome(executable_path=self.webdriver_path)
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
            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links:
                time.sleep(30)
            src = self.driver.page_source
            soup=BeautifulSoup(src,'html.parser')
            return src,soup

        def aruba(soup):
            find_aruba = soup.find_all('span', class_='arubaTag')
            #print(find_aruba)
            if find_aruba:
                print("This site",self.driver.current_url)
                return True
            return False


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
        #list_of_links=f.read().splitlines()
        list_of_links = ['https://partner.hpe.com','https://partner.hpe.com/group/prp/hpe-partner-ready-vantage','https://partner.hpe.com/group/prp/aruba-service-managed-services']
        #print(list_of_links)
        #pass links not to be checked paths here
        all_links_trans = filter(list_of_links,self.links_not_to_be_checked)
        # print("to runtrans",all_links_trans)
        all_links_empty = filter(list_of_links,self.not_to_check_links)
        # print("to runempty",all_links_empty)
        #print(all_links_empty,all_links_trans)

        errors = {}
        epterrors=[]
        aruba_links = set()
        # for link in list_of_links:
        #     #print(link)
        #     src,soup = integrate(link)
        #     #print(src,'#################')
            
        #     if aruba(soup):
        #         aruba_links.add(link)
        
        for link in list_of_links:
            src,soup = integrate(link)
            aruba_bool = aruba(soup)
            #print("HEY",aruba_bool)
            #print("LINK",link)
            if aruba_bool:

                if (link!='https://partner.hpe.com' and link!='https://partner.hpe.com/group/prp' and link!='https://partner.hpe.com/group/prp/home'):                    
                        
                        aruba_links.add(link)
         
        epterrors = [err for err in epterrors if err!='']
        # print(epterrors)
        write_excel(epterrors)
        # print(errors,type(errors))
        write_excel(errors)

            

        with open(self.aruba_links_path, 'w') as filehandle:
                for listitem in aruba_links:
                        filehandle.write('%s\n' % listitem)

       
        
    def tearDown(self):
        self.driver.close()
        df=pd.read_excel(self.translation_report_path)
        dff=pd.read_excel(self.emptypage_report_path)
        if len(df)>0:
            work.work_alloc_execute(self.translation_report_path,'Fixers_list.xlsx',self.aruba_links_path)
        if len(dff)>0:
            work.work_alloc_execute(self.emptypage_report_path,'Fixers_list.xlsx',self.aruba_links_path)

credentials=[#['demo_na_proximity@pproap.com', 'ExperiencePRP!', 'NA', 'USA', 'English', 'CTDB'],
['demo_italian_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
['demo_turkish_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
['demo_ukeng_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'UK', 'English', 'T2A'],['demo_french_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'ExperiencePRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
['demo_emea_platinum@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'T2'],
['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],['demo_spanisheu_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
['demo_japanese_jp_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
['demo_simplified_cn_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'China', 'Chinese', 'T2'],
['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]
for acc in credentials:
    Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
    #Firstrun.text_extract()
    Firstrun.setUp()
    Firstrun.test_load_home_page()
    Firstrun.parent()
    Firstrun.tearDown()
    print("going into the next account")
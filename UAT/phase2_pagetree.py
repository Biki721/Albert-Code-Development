from ast import main
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, TimeoutException,ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import time
import SelectCertificate
import VaultSample
import work
import ast
import win32com.client as win32
from bs4 import BeautifulSoup

class PRP():
    base_url='https://partner.hpe.com'
    webdriver_path="Webdrivers\\chromedriver.exe"
    # f= open('delayed_loading.txt',"r+")
    delayed_loading_links =work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    # breadcrumb_file=open("breadcrumb_links.txt",'r')
    breadcrumblinks=work.doc_reader("breadcrumb_links.docx")
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    absurd_links =work.doc_reader("absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']
    print(absurd_links)
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
        
    
    def setUp(self):
        webdriver_path = "Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()  
        self.driver=webdriver.Chrome(executable_path=self.webdriver_path)
        self.driver.maximize_window()  
        self.wait = WebDriverWait(self.driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
  

    def test_load_home_page(self):

        self.driver.get(self.base_url)
        print('LINE 64 -------------------------------------------------------------------')
        
        login_title = self.driver.title
        self.wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(self.username)
        self.wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(self.password)
        self.wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click()
        try:
            WebDriverWait(self.driver,15).until(EC.title_contains('Home'))
        except TimeoutException:
            print('\nTIMEOUT EXCEPTION-------->HOME PAGE FAILED TO LOAD')
        print('LINE 74------------------------')

        new_title = self.driver.title

        if login_title==new_title:
            print('DEMO ACCOUNT',self.username,'FAILED TO LOGIN')
            self.email(self.login_errmsg)

            return False
        
        # driver=self.driver
        # wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        # driver.get(self.base_url)
        # wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(self.username)
        # wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(self.password)
        # wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click()

        def detect_lang(self):
            self.driver.get('https://partner.hpe.com/group/prp/settings')
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
                self.wait.until(EC.element_to_be_clickable((By.ID, "personal-save-personal-cancel"))).click()
                self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn-toolbar-button btn btn-default yui3-widget aui-button yui3-aui-button yui3-aui-button-content cancelButton tertiaryButton btn-default btn cancelButton tertiaryButton btn-default btn-content yui3-aui-button-focused"))).click()
                #self.email(self.lang_errmsg)

            except TimeoutException:
                print('COULD NOT FIND BUTTON')

        self.disp_lang = detect_lang(self)
        if self.disp_lang != self.language:
            change_lang(self)
            self.driver.close()

        return True
    

           
    def email(self, errmsg):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        #mail.To = 'pranav-m.bhat@hpe.com;somaiah.kodimaniyanda-lava@hpe.com;aravind.shivakumar@hpe.com;liliana.tarca@hpe.com;srividya-d@hpe.com;ragul.subramani@hpe.com;marina.melcioiu@hpe.com;kalaivanan.a@hpe.com;mohammed.imran4@hpe.com;peng.wang3@hpe.com;probles@hpe.com;weiwei.shao@hpe.com;xiaojie.feng@hpe.com;salazar-guevara@hpe.com'
        #mail.To = 'pranav-m.bhat@hpe.com;rohitashwyo.dutta-chowdhury@hpe.com'
        mail.To = 'pranav-m.bhat@hpe.com'
        mail.Subject = errmsg[0]
        mail.Body = errmsg[1]
        mail.Send()   
        
    def filter_breadcrumbs(self,link):
        status = True
        for li in self.breadcrumb_prefix:
            if link.startswith(li):
                status = False
        if link in self.breadcrumblinks:
            status = False
        return status

    def scrape(self,queue,internal,external,allurls,doclinks,tree_dict):
                driver=self.driver
                print('LINE 146---------------------')
                login_bool = self.test_load_home_page()  #Checks for login error
                if login_bool is False:
                    return False, False, False, False, False

                wait = WebDriverWait(driver,30,ignored_exceptions=[TimeoutException])
                while queue:
                    link = queue.pop(0).strip().strip('\n')
                    if '/documents' in link or '/esm' in link or '.pdf' in link or '.xlsx' in link or '.zip' in link:
                        doclinks.add(link)
                        allurls.add(link)
                        continue
                    if link.startswith('http'):
                        allurls.add(link)
                        if (link.startswith('https://partner.hpe.com')):
                            
                            tree_dict.update({link:[]})
                            try:
                                driver.get(link)
                                if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                                    try:
                                        wait.until(EC.visibility_of_all_elements_located((By.ID, 'disBtn')))
                                    except:
                                        pass
                                if link in self.absurd_links:
                                    time.sleep(15)
                                    
                                

                            except:
                                pass
                            if self.filter_breadcrumbs(link):
                                internal.add(link)
                            try:
                                ahref = driver.find_elements_by_tag_name("a")
                                inputval = driver.find_elements_by_css_selector("input")
                                for ele in ahref:
                                    url = ele.get_attribute("href")
                                    #print("url",url)
                                    if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url :
                                        if not url.startswith('http') and not url.startswith('https://partner.hpe.com') and ('article-display-page?' in url or 'group/prp' in url):
                                            if url.startswith("/group/prp"):
                                                url='https://partner.hpe.com'+url
                                            else:
                                                url = 'https://partner.hpe.com/group/prp'+url
                                        if url.startswith('http'):
                                            tree_dict[link].append(url)
                                        queue.append(url)
                                for ele in inputval:
                                    url = ele.get_attribute("value")
                                    if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url:
                                        if not url.startswith('http') and not url.startswith('https://partner.hpe.com') and ('article-display-page?' in url or 'group/prp' in url):
                                            if url.startswith("/group/prp"):
                                                url='https://partner.hpe.com'+url
                                            else:
                                                url = 'https://partner.hpe.com/group/prp'+url
                                        if url.startswith('http'):
                                            tree_dict[link].append(url)
                                        queue.append(url)
                                queue = list(set(queue))#contains lotta repeated crap like "false","javascript:void"
                                tree_dict[link] = list(set(tree_dict[link]))
                            except:
                                continue     
                                
                        else:
                         
                            if self.filter_breadcrumbs(link):
                                external.add(link)
                return allurls,internal,external,doclinks,tree_dict

    def reverse_dict_builder(self,treedict,allurls):
        keys=list(treedict.keys())
        values=list(treedict.values())
        revdict={}
        for p in allurls:
            index=[]
            sources=[]
            actual_sources=set()
            for ele in values:
                if p in ele or p.strip() in ele:
                    index.append(values.index(ele))
            for ele in index:
                sources.append(keys[ele])
            actual_sources=set(sources)
            revdict.update({p:list(actual_sources)})

        return revdict
    
    def scrapecall_writetrees(self):
        internal = set()
        external = set()
        docs = set()
        all_links = set()
        tree_dict = {}
        queue = [self.base_url]
        all_links, internal, external, docs, tree_dict = self.scrape(queue,internal,external,all_links,docs,tree_dict)

        if all_links is False: #If login fails, return false
            return False

        with open(self.page_tree_path, 'w') as filehandle:
                for item in internal:
                    if item.startswith('https://partner.hpe.com/group/prp'):
                        filehandle.write('%s\n' % item)
        with open(self.external_urls_path, 'w') as filehandle:
                for listitem in external:
                        filehandle.write('%s\n' % listitem) 
        with open(self.doc_link_path, 'w') as filehandle:
                for listitem in docs:
                        filehandle.write('%s\n' % listitem)
        #print(type(tree_dict),type(all_links))
        revdict=self.reverse_dict_builder(tree_dict,all_links)
        with open(self.reverse_dict_path,'w') as filehandle:
            filehandle.write(str(revdict))
        # print(len(all_links),len(internal),len(external))

        return True
    
  
    

    
    def tearDown(self):
        self.driver.close()





# credentials=[['demo_french_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'France', 'French', 'T2'],
# ['demo_la_distributor@pproap.com', 'ExperiencePRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
# credentials=[['demo_spanisheu_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]
# credentials=[['demo_na_proximity@pproap.com', 'ExperiencePRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# ['demo_turkish_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
# ['demo_ukeng_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'UK', 'English', 'T2A'],['demo_french_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'ExperiencePRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],['demo_spanisheu_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]


credentials = [['demo_ukeng_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'UK', 'English', 'Distri']]
#         #    ['demo_english_sg_oem@pproap.com', 'ExperiencePRP!', 'APJ', 'Singapore', 'English', 'OEM'],
#            ['demo_na_distributor@pproap.com', 'ExperiencePRP!', 'NAR', 'USA', 'English', 'Distri']]
for acc in credentials:
    print(acc)
    Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
    Firstrun.setUp()
    Firstrun.scrapecall_writetrees()
    Firstrun.tearDown()
    print("going into the next account")

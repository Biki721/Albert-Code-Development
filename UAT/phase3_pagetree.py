from ast import main
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, TimeoutException,ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
import time
from SelectCertificate import authenticate_with_certificate
import VaultSample
import work
import ast
from selenium.webdriver.chrome.service import Service

class PRP():
    base_url="https://partner.hpe.com"
    delayed_loading_links =work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    breadcrumblinks=work.doc_reader("breadcrumb_links.docx")
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    # print('BREADCRUMBS',breadcrumblinks)
    absurd_links = work.doc_reader("absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']
    # print(absurd_links)
    breadcrumb_prefix=work.doc_reader("Breadcrumb_Prefix.docx")
    breadcrumb_prefix=[s.strip() for s in breadcrumb_prefix if s!='']
    # print('BREADCRUMB PREFIX',breadcrumb_prefix)
    # breadcrumb_prefix=["https://partner.hpe.com/group/prp/settings-old",'https://partner.hpe.com/group/prp/price-communications','https://partner.hpe.com/group/prp/reports']
    

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
    
    def setUp(self):
        webdriver_path = "Webdrivers\\chromedriver.exe"
        service = Service(webdriver_path)
        self.driver = webdriver.Chrome(service=service)
        self.driver.maximize_window()    

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
        self.test_load_home_page()
        wait = WebDriverWait(driver,30,ignored_exceptions=[TimeoutException])

        while queue:
            link = queue.pop(0).strip().strip('\n')
            if '/documents' in link or '/esm' in link or '.pdf' in link or '.xlsx' in link or '.zip' in link:
                doclinks.add(link)
                allurls.add(link)
                continue
            
            if link.startswith('http'):
                allurls.add(link)
                if (link.startswith("https://partner.hpe.com")):
                    
                    tree_dict.update({link:[]})
                    try:
                        driver.get(link)
                        # time.sleep(10)
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
                        # print('RANDOM')
                        # print(driver.page_source)
                        ahref = driver.find_elements(By.TAG_NAME,"a")
                        inputval = driver.find_elements(By.CSS_SELECTOR,"input")
                        for ele in ahref:
                            url = ele.get_attribute("href")
                            # print("url",url)
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url :
                                if not url.startswith('https://partner.hpe.com'):
                                    print(url)
                                    if url.startswith("/group/prp"):
                                        url='https://partner.hpe.com'+url
                                    else:
                                        url = 'https://partner.hpe.com/group/prp'+url
                                if url.startswith('http'):
                                    tree_dict[link].append(url)
                                queue.append(url)
                        for ele in inputval:
                            url = ele.get_attribute("value")
                            # print('random')
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url:
                                if not url.startswith('http') and not url.startswith('https://partner.hpe.com'):
                                    if url.startswith("/group/prp"):
                                        url='https://partner.hpe.com'+url
                                    else:
                                        url = 'https://partner.hpe.com/group/prp'+url
                                if url.startswith('http'):
                                    tree_dict[link].append(url)
                                queue.append(url)
                        queue = list(set(queue)) # contains lotta repeated crap like "false","javascript:void"
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
        all_links, internal, external,docs,tree_dict = self.scrape(queue,internal,external,all_links,docs,tree_dict)
        with open(self.page_tree_path, 'w') as filehandle:
                for item in internal:
                    if item.startswith("https://partner.hpe.com/group/prp"):
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
    
  
    

    
    def tearDown(self):
        self.driver.close()







# credentials=[['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],
# ['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD']]
# credentials=[['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]
# credentials=[['demo_na_proximity@pproap.com', 'Login2PRP!', 'NA', 'USA', 'English', 'CTDB'],
# ['demo_italian_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
# ['demo_turkish_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
#,['demo_french_solp@yopmail.com', 'Login2PRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'Login2PRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'Login2PRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'Login2PRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'Login2PRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'Login2PRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]


if __name__=='__main__':
    credentials = [['demo_spanisheu_distri@yopmail.com', 'Login2PRP!', 'EMEA', 'Spain', 'Spanish', 'Distri']]
                #    ['demo_korean_distributor@pproap.com','Login2PRP!','APJ','Korea','Korean','Distri']]
            # ['demo_na_distributor@pproap.com', 'Login2PRP!', 'NAR', 'USA', 'English', 'Distri']]

    for acc in credentials:
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        Firstrun.setUp()
        Firstrun.scrapecall_writetrees()
        Firstrun.tearDown()
        print("going into the next account")

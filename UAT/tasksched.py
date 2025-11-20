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

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"
    f= open('delayed_loading.txt',"r+")
    delayed_loading_links = f.read().splitlines()
    delayed_loading_links=[s.strip() for s in delayed_loading_links] 
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
        self.driver=webdriver.Chrome(executable_path=self.webdriver_path)
        self.driver.maximize_window()    

    def test_load_home_page(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click()      
        
        
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
                                if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                                    try:
                                        wait.until(EC.visibility_of_all_elements_located((By.ID, 'disBtn')))
                                    except:
                                        pass

                            except:
                                pass
                            internal.add(link)
                            try:
                                ahref = driver.find_elements_by_tag_name("a")
                                inputval = driver.find_elements_by_css_selector("input")
                                for ele in ahref:
                                    url = ele.get_attribute("href")
                                    #print("url",url)
                                    if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and 'notifications?p_p_id=com_liferay' not in url :
                                        if not url.startswith('http') and not url.startswith('https://partner.hpe.com') and ('article-display-page?' in url or 'group/prp' in url):
                                            url = 'https://partner.hpe.com/group/prp'+url
                                        if url.startswith('http'):
                                            tree_dict[link].append(url)
                                        queue.append(url)
                                for ele in inputval:
                                    url = ele.get_attribute("value")
                                    if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and 'notifications?p_p_id=com_liferay' not in url:
                                        if not url.startswith('http') and not url.startswith('https://partner.hpe.com') and ('article-display-page?' in url or 'group/prp' in url):
                                            url = 'https://partner.hpe.com/group/prp'+url
                                        if url.startswith('http'):
                                            tree_dict[link].append(url)
                                        queue.append(url)
                                queue = list(set(queue))#contains lotta repeated crap like "false","javascript:void"
                                tree_dict[link] = list(set(tree_dict[link]))
                            except:
                                continue     
                                
                        else:
                                external.add(link)
                return allurls,internal,external,doclinks,tree_dict
    def reverse_dict_builder(treedict,allurls):
       
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
                    filehandle.write('%s\n' % item)
        with open(self.external_urls_path, 'w') as filehandle:
                for listitem in external:
                        filehandle.write('%s\n' % listitem) 
        with open(self.doc_link_path, 'w') as filehandle:
                for listitem in docs:
                        filehandle.write('%s\n' % listitem)
        
        revdict=self.reverse_dict_builder(tree_dict,all_links)
        with open(self.reverse_dict_path,'w') as filehandle:
            filehandle.write(str(revdict))
        print(len(all_links),len(internal),len(external))
    

    
    def tearDown(self):
        self.driver.close()







# credentials = [['demo_emea_distributor@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'Distri']]
 
# for acc in credentials:
#     Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
#     Firstrun.setUp()
#     Firstrun.scrapecall_writetrees()
#     Firstrun.tearDown()
#     print("going into the next account")

       
            
                
        

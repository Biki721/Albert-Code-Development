from ast import main
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, SessionNotCreatedException, StaleElementReferenceException, TimeoutException,ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from SelectCertificate import authenticate_with_certificate
import VaultSample
import work_phase_3 as work
import ast
from selenium.webdriver.chrome.service import Service
import threading
import pygetwindow as gw
import pyautogui
from pynput.keyboard import Key, Controller
from concurrent.futures import ThreadPoolExecutor

class PRP():
    base_url="https://marketingpro.hpe.com"
    delayed_loading_links =work.doc_reader("marketingpro_delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    breadcrumblinks=work.doc_reader("marketingpro_breadcrumb_links.docx")
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']
    # print('BREADCRUMBS',breadcrumblinks)
    absurd_links = work.doc_reader("marketingpro_absurd_links.docx")
    absurd_links=[s.strip() for s in absurd_links if s!='']
    # print(absurd_links)
    breadcrumb_prefix=work.doc_reader("marketingpro_breadcrumb_prefix.docx")
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
        self.page_tree_path='MarketingProPageTrees\\PageTree{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        #self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.doc_link_path ='MarketingPro DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.reverse_dict_path='MarketingPro Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.external_urls_path='MarketingPro External Urls\\External{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.mrp_links = None
        self.lock = threading.Lock()
        

    def setUp(self):
        
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) 
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()    

    def test_load_home_page(self):
        
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "password-sign-in"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, 'onepass-submit-btn'))).click()
        time.sleep(10)
        try:
            elem = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form19"]/div[2]/div[2]/div[2]/a')))
            elem.click()
            time.sleep(20) 
        except:
            pass

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
                if not (link.startswith("https://partner.hpe")):
                    allurls.add(link)
                if (link.startswith("https://marketingpro")):
                    
                    tree_dict.update({link:[]})
                    try:
                        driver.get(link)
                        time.sleep(10)
                        if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                            try:
                                wait.until(EC.visibility_of_all_elements_located((By.ID, 'disBtn')))
                            except:
                                pass
                        if link in self.absurd_links:
                            time.sleep(15)
                            
                    except:
                        pass

                    # if self.filter_breadcrumbs(link):
                    
                    internal.add(link)

                    try:
                        # print('RANDOM')
                        # print(driver.page_source)
                        ahref = driver.find_elements(By.TAG_NAME,"a")
                        inputval = driver.find_elements(By.CSS_SELECTOR,"input")
                        for ele in ahref:
                            url = ele.get_attribute("href")
                            # print("url",url)
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url  and 'partner.hpe' not in url and 'group/prp' not in url:
                                # if not url.startswith('http') and not url.startswith('https://marketingpro.hpe.com') and ('article-display-page?' in url or 'group/site' in url):
                                if url.startswith('https') or url.startswith('http'):
                                    # print(url)
                                    tree_dict[link].append(url)
                                # if url.startswith('http'):
                                #     tree_dict[link].append(url)
                                queue.append(url)
                          

                        for ele in inputval:
                            url = ele.get_attribute("value")
                            # print('random')
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url and 'partner.hpe' not in url and 'group/prp' not in url:
                                # if not url.startswith('http') and not url.startswith('https://marketingpro.hpe.com') and ('article-display-page?' in url or 'group/site' in url):
                                if url.startswith('https') or url.startswith('http'):
                                    # print(url)
                                    tree_dict[link].append(url)
                                # if url.startswith('http'):
                                #     tree_dict[link].append(url)
                                queue.append(url)
                        queue = list(set(queue)) # contains lotta repeated crap like "false","javascript:void"
                        tree_dict[link] = list(set(tree_dict[link]))
                    except:
                        continue     
                        
                else:
                    if 'partner.hpe.com' not in link or 'www.hpe.com' not in link:
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
        self.mrp_links = len(internal)+len(all_links)+len(external)+len(docs)
        with open(self.page_tree_path, 'w') as filehandle:
                for item in internal:
                    if item.startswith("https://marketingpro"):
                        filehandle.write('%s\n' % item)
        with open(self.external_urls_path, 'w') as filehandle:
                for listitem in external:
                        filehandle.write('%s\n' % listitem) 
        with open(self.doc_link_path, 'w') as filehandle:
                for listitem in docs:
                        filehandle.write('%s\n' % listitem)
        # print(type(tree_dict),type(all_links))
        revdict=self.reverse_dict_builder(tree_dict,all_links)
        with open(self.reverse_dict_path,'w') as filehandle:
            filehandle.write(str(revdict))
        # print(len(all_links),len(internal),len(external),len(revdict))
    
  
    

    
    def tearDown(self):
        self.driver.close()

def run_account(account):
    try:
        prp = PRP(*account)
        prp.setUp()
        prp.scrapecall_writetrees()
        prp.tearDown()
        print(f"Finished processing: {account[0]}")
    except Exception as e:
        print(f"Error in processing {account[0]}: {e}")

if __name__=='__main__':
    
    credentials = [
        ['demo_french_distri@yopmail.com','Want2seePRP!','EMEA','France','French','Distri'],
        ['demo_emea_platinum@pproap.com', 'Want2seePRP!', 'EMEA', 'Germany', 'German','T2'],
        ['demo_italian_distri@yopmail.com', 'Want2seePRP!', 'EMEA', 'Italy', 'Italian', 'Distri'],
        ['demo_turkish_solp@yopmail.com', 'Want2seePRP!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
        ['demo_ukeng_distri@yopmail.com', 'Want2seePRP!', 'EMEA', 'UK', 'English', 'Distri'],
        # ['demo_la_platinum@pproap.com', 'Want2seePRP!', 'NAR', 'MEXICO', 'Spanish', 'T2'],
        ['demo_h3c@pproap.com', 'Want2seePRP!', 'APJ', 'China', 'Chinese', 'T2'],
        ['demo_na_distributor@pproap.com', 'Want2seePRP!', 'NAR', 'USA', 'English', 'Distri'],
        ['demo_traditional_cn_distributor@pproap.com','Want2seePRP!','APJ','Taiwan','Taiwai','Distri'],
        ['demo_indonesian_distributor@pproap.com', 'Want2seePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri'],
        ['demo_japanese_distributor@pproap.com','Want2seePRP!','APJ','Japan','Japanese','Distri'],
        ['demo_korean_kr_t2solutionprovider@pproap.com', 'Want2seePRP!', 'APJ', 'Korea', 'Korean', 'T2']
    ]

    # Adjust max_workers based on your system capability (e.g., RAM, CPU, browser limits)
    with ThreadPoolExecutor(max_workers=6) as executor:
        executor.map(run_account, credentials)

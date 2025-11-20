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
import pyautogui
import pygetwindow as gw
import threading
from selenium.webdriver.chrome.service import Service
from pynput.keyboard import Key, Controller
from selenium.webdriver.chrome.options import Options

class PRP():
    base_url="https://internal.it.hpe.com/"
    webdriver_path="Webdrivers\\chromedriver.exe"
    # f= open('delayed_loading.txt',"r+")
    delayed_loading_links =work.doc_reader("delayed_loading.docx")
    delayed_loading_links=[s.strip() for s in delayed_loading_links if s!='']
    # breadcrumb_file=open("breadcrumb_links.txt",'r')

    # breadcrumblinks=work.doc_reader("breadcrumb_links.docx") # UNCOMMENT THIS IF THE AD HOC REQUEST REQUIRES ALBERT TO IGNORE BREADCRUMB LINKS

    breadcrumblinks = []
    breadcrumblinks=[s.strip() for s in breadcrumblinks if s!='']

    # absurd_links =work.doc_reader("absurd_links.docx") # UNCOMMENT THIS IF THE AD HOC REQUEST REQUIRES ALBERT TO IGNORE ABSURD LINKS

    absurd_links = []
    absurd_links=[s.strip() for s in absurd_links if s!='']
    # print(absurd_links)

    # breadcrumb_prefix=work.doc_reader("Breadcrumb_Prefix.docx") # UNCOMMENT THIS IF THE AD HOC REQUEST REQUIRES ALBERT TO IGNORE BREADCRUMB PREFIX LINKS

    breadcrumb_prefix = [] 
    breadcrumb_prefix=[s.strip() for s in breadcrumb_prefix if s!='']

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
        self.page_tree_path='Page Trees\\AD_HOC_PageTree_Internal.txt'
        self.tree_dict_path='Tree Dicts\\AD_HOC_TreeDict.txt'
        self.doc_link_path ='DocumentLinks\\AD_HOC_Doclinks.txt'
        self.reverse_dict_path='Reverse Dicts\\AD_HOC_RevDict.txt'
        self.external_urls_path='External Urls\\AD_HOC_External.txt'
        self.iframe_links_path = ''


    def setUp(self): 
        # webdriver_path = "Webdrivers\\chromedriver.exe"
        # service = Service(webdriver_path)
        chrome_options = Options()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()  
    
    def login_internal(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        self.driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaEmailInput"))).send_keys(self.username)
        # time.sleep(25)
        wait.until(EC.element_to_be_clickable((By.ID, "oktaSignInBtn"))).click()
        # wait.until(EC.element_to_be_clickable((By.ID, 'p_p_id_com_liferay_login_web_portlet_LoginPortlet_'))).click()
        time.sleep(10)
  
    def filter_breadcrumbs(self,link):
        status = True
        for li in self.breadcrumb_prefix:
            if link.startswith(li):
                status = False
        if link in self.breadcrumblinks:
            status = False
        return status

    def scrape(self,queue,internal,external,allurls,doclinks,tree_dict,links_iframes_dict):
        driver=self.driver
        self.login_internal()
        time.sleep(10)
        driver.get('https://partner.hpe.com')
        print("Loaaded the link")
        
        time.sleep(20)
        wait = WebDriverWait(driver,30,ignored_exceptions=[TimeoutException])
        while queue:
            link = queue.pop(0).strip().strip('\n')
            print('link', link)
            print("line 99")
            
            if '/documents' in link or '/esm' in link or '.pdf' in link or '.xlsx' in link or '.zip' in link:
                doclinks.add(link)
                allurls.add(link)
                continue
            
            if link.startswith('http'):
                
                allurls.add(link)
                # print('line 142')
                if (link.startswith("https://partner.hpe.com")) or (link.startswith('https://internal.it.hpe.com')):
                        
                    tree_dict.update({link:[]})
                    links_iframes_dict[link] = []
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
                        ahref = driver.find_elements(By.TAG_NAME,"a")
                        inputval = driver.find_elements(By.CSS_SELECTOR,"input")
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        for iframe in iframes:
                            
                            iframe_src = iframe.get_attribute("src")
                            print('iframe link: ',iframe_src)
                            if iframe_src and iframe_src.startswith("http") and not iframe_src.startswith("https://partner.hpe.com") and 'internal.it.hpe.com' not in iframe_src:
                                if self.filter_breadcrumbs(iframe_src):
                                    print('adding iframe links')
                                    external.add(iframe_src)
                                tree_dict[link].append(iframe_src)
                                try:
                                    links_iframes_dict[link].append(iframe_src)
                                    print("added")
                                except:
                                    links_iframes_dict[link].append(None)
                                    print('notAdded')

                        for ele in ahref:
                            url = ele.get_attribute("href")
                            #print("url",url)
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url :
                                
                                if url.startswith('http') or 'partner.hpe.com' or 'internal.it.hpe.com' in url:
                                    tree_dict[link].append(url)
                                queue.append(url)
                        for ele in inputval:
                            url = ele.get_attribute("value")
                            if url is not None and url.strip()!='' and url not in allurls and 'login' not in url and 'logout' not in url and '#' not in url and '?p_p_id=com' not in url:
                                
                                if url.startswith('http') or 'partner.hpe.com' or 'internal.it.hpe.com' in url:
                                    tree_dict[link].append(url)
                                queue.append(url)
                        queue = list(set(queue)) # contains lotta repeated crap like "false","javascript:void"
                        tree_dict[link] = list(set(tree_dict[link]))
                    except:
                        continue     
                        
                else:
                    
                    if self.filter_breadcrumbs(link):
                        external.add(link)
                
        return allurls,internal,external,doclinks,tree_dict,links_iframes_dict
    

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
        links_iframes_dict = {}
        queue = ['https://partner.hpe.com']
        all_links, internal, external,docs,tree_dict,links_iframes_dict = self.scrape(queue,internal,external,all_links,docs,tree_dict,links_iframes_dict)
        with open(self.page_tree_path, 'w') as filehandle:
                for item in internal:
                    if item.startswith("https://partner.hpe.com") or item.startswith('https://internal.it.hpe.com'):
                        filehandle.write('%s\n' % item)
        with open(self.external_urls_path, 'w') as filehandle:
                for listitem in external:
                        filehandle.write('%s\n' % listitem) 
        with open(self.doc_link_path, 'w') as filehandle:
                for listitem in docs:
                        filehandle.write('%s\n' % listitem)
        with open(self.tree_dict_path, 'w') as filehandle:
             filehandle.write('%s\n'%tree_dict)
        #print(type(tree_dict),type(all_links))
        revdict=self.reverse_dict_builder(tree_dict,all_links)
        with open(self.reverse_dict_path,'w') as filehandle:
            filehandle.write(str(revdict))

        with open('collected_links.txt', 'w') as f:
            f.write("Links and Iframes:\n")
            for link, iframes in links_iframes_dict.items():
                for iframe in iframes:
                    f.write(f"{link}: {iframe}\n")
        # print(len(all_links),len(internal),len(external))
    
  
    

    
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
#,['demo_french_solp@yopmail.com', 'ExperiencePRP!', 'EMEA', 'France', 'French', 'T2'],['demo_la_distributor@pproap.com', 'ExperiencePRP!', 'LAR', 'Mexico', 'LARSpanish', 'Distri'],
# ['demo_emea_platinum@pproap.com', 'ExperiencePRP!', 'EMEA', 'Germany', 'German', 'T2'],
# ['demo_distributor_lar@pproap.com', 'ExperiencePRP!', 'LAR', 'Brazil', 'Portugese', 'CTD'],['demo_spanisheu_distri@yopmail.com', 'ExperiencePRP!', 'EMEA', 'Spain', 'Spanish', 'Distri'],
# ['demo_japanese_jp_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'Japan', 'Japanese', 'T2'],
# ['demo_simplified_cn_t2solutionprovider@pproap.com', 'ExperiencePRP!', 'APJ', 'China', 'Chinese', 'T2'],
# ['demo_indonesian_distributor@pproap.com', 'ExperiencePRP!', 'APJ', 'Indonesia', 'Indonesian', 'Distri']]


if __name__=='__main__':
    credentials = [['bot.dec-d001a@hpe.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2']]
            # ['demo_na_distributor@pproap.com', 'ExperiencePRP!', 'NAR', 'USA', 'English', 'Distri']]

    for acc in credentials:
        Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
        Firstrun.setUp()
        # time.sleep(10)
        # Firstrun.test_internal_page()
        Firstrun.scrapecall_writetrees()
        Firstrun.tearDown()
        print("going into the next account")

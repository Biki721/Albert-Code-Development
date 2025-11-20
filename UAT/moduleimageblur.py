from pywinauto.handleprops import style
from selenium import webdriver
from bs4 import BeautifulSoup
import cv2
import matplotlib.pyplot as plt
import datetime

from pylab import rcParams
from IPython.display import Image
rcParams['figure.figsize'] = 8, 16
import requests
import os
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support.ui import WebDriverWait
import SelectCertificate
from selenium.webdriver.support import expected_conditions as EC
import VaultSample
import work
import pandas as pd
from selenium.webdriver.common.by import By

class PRP():
    base_url="https://partner.hpe.com"
    webdriver_path="Webdrivers\\chromedriver.exe"

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
        self.report_path='Reports\\Image_Blur_{r}_{c}_{l}_{a}.xlsx'.format(r=self.region,c=self.country,a=self.account_type,l=self.language)
        self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)

    
    
    def setUp(self):
        self.driver=webdriver.Chrome(executable_path=self.webdriver_path)
        self.driver.maximize_window()
        self.driver.implicitly_wait(2)

    def test_load_home_page(self):
        driver=self.driver
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
        driver.get(self.base_url)
        wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(self.username)
        wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(self.password)
        wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click()
        # try:
        #     SelectCertificate.authenticate_with_certificate('')
        #     SelectCertificate.handle_pin_prompt('')
        # except:
        #     pass
        
    def test_image_blurriness(self):    
        
        def variance_of_laplacian(image):
            return cv2.Laplacian(image, cv2.CV_64F).var()
    
        def checkblurriness(imagePath):
          threshold=5
          image = cv2.imread(imagePath)
          gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          fm = variance_of_laplacian(gray)
        #   print("oihioh",fm)
          if fm > threshold:
            #print("Not blurry")
            text ="Not blurry"
          if fm < threshold:
            #print("Blurry")
            text = "Blurry"
          return text
        def screenshotandcheck(driver,weburl,image_links):
            text=''
            #print("**********",weburl)
            #driver.get(weburl)
            #element = driver.find_element_by_tag_name('body')
            for i in range(len(image_links)):
                try:
                    driver.get(image_links[i])
                    driver.get_screenshot_as_file("screenshot.png")
                    text = checkblurriness("screenshot.png")
                    if (text=="Not blurry"):
                        os.remove("screenshot.png")
                    else:
                        print("blurry image in",weburl)
                        return "Blurry",image_links[i]
                except:
                    continue
            return text,'None'
        
        def get_all_image_urls(weblink):
            driver=self.driver
            try:
                driver.get(weblink) 
            except:
                print("timeout",weblink)
                pass
            div_tags = driver.find_elements_by_css_selector("div")
            img_tags = driver.find_elements_by_css_selector("img")
            div_tags.extend(img_tags)
            all_image_urls_for_page=[]
            images_minus_exclusiontags=[]
            for i in div_tags:
                    try:
                        if (i.get_attribute('style')):
                            style_content = i.get_attribute('style')
                            if "url" in style_content:
                                temp=style_content.index("url")
                                style_content = style_content[temp:]
                                # print(style_content[style_content.find("(")+1:style_content.find(")")])
                                if "icon" not in style_content and ".svg" not in style_content and "Icon" not in style_content and "gif" not in style_content:
                                    if "cdn1" not in style_content:
                                        all_image_urls_for_page.append("https://partner.hpe.com"+style_content[style_content.find("(")+2:style_content.find(")")-1])
                        elif (i.get_attribute('src')):
                            content = i.get_attribute('src')
                            # print(content)
                            if 'icon' not in content and "Icon" not in content:
                                if ".svg" not in content and "gif" not in content:
                                    all_image_urls_for_page.append(content)
                    except:
                        print('Some error')
            for ele in all_image_urls_for_page:
                if "cdn" not in ele and "icon" not in ele and "Icon" not in ele and ".svg" not in ele and ".gif" not in ele and "osv" not in ele:
                    images_minus_exclusiontags.append(ele)
                 
            return screenshotandcheck(driver,weblink,images_minus_exclusiontags)
            
        
        def call_screenshot_check():
            f = open(self.page_tree_path)
            all_links=list(f.readlines())
            # print(all_links)
            output={}
            all_imglinks=[]
            for i in range(len(all_links)):
                # print(all_links[i])
                match,imglink = get_all_image_urls(all_links[i])
                # content=match.split()[0]
                if (match=="Blurry") and imglink not in all_imglinks:

                    output.update({all_links[i]:imglink})
                    all_imglinks.append(imglink)
            if (output):
                write_excel(list(output.keys()),list(output.values()))
            return
        def write_excel(matches,imglinks):
            if "cdn1" in imglinks:
                pass
            else:
                account=self.username
                region = self.region
                country=self.country
                language=self.language
                issueid = [i+1 for i in range(len(matches))]
                category = ["Image blurriness"]*len(matches)
                status = ["New"]*len(matches)
                comments = ["-"]*len(matches)
                description = ["Image link specified in column Link is blurry"]*len(matches)
                time = [datetime.datetime.now()]*len(matches)
                result = {'Issue ID':issueid,'Demo Account': account,'Category':category,'Link':matches,'Error Link':imglinks,'Description':description,'Time Identified':time,'Region':region,'Country':country,'Language':language,'Fixers':"none",'Mail ID':"none",'Status':status,'Comments':comments}
                df = pd.DataFrame.from_dict(result)
                print(df)
                df.to_excel(self.report_path)
            print("excel created")
            return

        self.test_load_home_page()
        call_screenshot_check()
            
        
    def tearDown(self):
        self.driver.close()
        try:
            df=pd.read_excel(self.report_path)
            if len(df)>0:
                work.work_alloc_execute(self.report_path,'Fixers_list.xlsx')
        except:
            pass


# credentials=[["mapdummypartner@yopmail.com","ExperiencePRP!","EMEA",'Croatia',"English","MAP"]]
credentials=VaultSample.result
print(credentials)
for acc in credentials:
    print("into image check module\n")
    print(acc[0])
    Firstrun=PRP(acc[0],acc[1],acc[2],acc[3],acc[4],acc[5])
    Firstrun.setUp()
    Firstrun.test_image_blurriness()
    Firstrun.tearDown()
    print("going into the next account")
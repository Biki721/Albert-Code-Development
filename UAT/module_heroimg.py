import work_phase_3 as work
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
import re

test_links = [
    'https://partner.hpe.com',
    'https://partner.hpe.com/group/prp/article-display-page?id=441293008',
    'https://partner.hpe.com/group/prp/article-display-page?id=808708552',
    'https://partner.hpe.com/group/prp/tools-catalog',
    'https://partner.hpe.com/group/prp/promotions',
    'https://partner.hpe.com/group/prp/news',
    'https://partner.hpe.com/group/prp/new-order-request',
    'https://partner.hpe.com/group/prp/article-display-page?id=558986418'
]
webdriver_path="Webdrivers\\chromedriver.exe"
username = 'demo_emea_distributor@pproap.com'
password = 'ExperiencePRP!'

def check(links):
    driver=webdriver.Chrome(executable_path=webdriver_path)
    driver.maximize_window()  
    driver.get('https://partner.hpe.com')  
    wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
    wait.until(EC.element_to_be_clickable((By.ID, "USER"))).send_keys(username)
    wait.until(EC.element_to_be_clickable((By.ID, "PASSWORD"))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.ID, "_com_liferay_login_web_portlet_LoginPortlet_sign-in-btn"))).click() 

    for i in links:
        print('***********',i,'************')
        driver.get(i)
        src = driver.page_source
        soup=BeautifulSoup(src,'html.parser')
        # print(soup)
        img = hero_check(soup)
        if img:
            print('HERO IMG PRESENT')
        else:
            print('NO IMAGE')

    driver.close()

def hero_check(soup):
    header_img = soup.find_all('div', class_='header-image')
    article_img = soup.find_all('div', class_='articleImg')
    program_img = soup.find_all('div', class_='pprPanner')

    url_pattern = r'url\((.*?)\)'

    if header_img or article_img or program_img:
        for element in header_img+article_img+program_img:
            # print(element)
            style_attr = element.get('style')
            # src_attr = element.get('img src')
            # print('SRC:',src_attr)


            if style_attr:
                urls = re.findall(url_pattern, style_attr)
                for url in urls:
                    if '.png' in url or '.jpg' in url or '.jpeg' in url:
                        return True

            elif header_img:
                src_attr = str(header_img)
                # print(src_attr)
                if src_attr:
                    if '.png' in src_attr or '.jpg' in src_attr or '.jpeg' in src_attr:
                        return True
                    
            # elif program_img:
            #     urls = re.findall(url_pattern, style_attr)
            #     print(urls)
            #     for url in urls:
            #         if '.png' in url or '.jpg' in url or '.jpeg' in url:
            #             return True        

        return False
    
    else:
        return True
                        



if __name__=='__main__':
    check(test_links)
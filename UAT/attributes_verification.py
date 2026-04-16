import pyautogui
import threading
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException, TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from SelectCertificate import authenticate_with_certificate
import time

def prp_internal(url, driver, wait):
    timeout = 1200
    start_time = time.time()
    internal_login_url = 'https://partner.hpe.com/login?TYPE=33554433&REALMOID=06-0005bd8e-1920-1c08-acd2-70ef10c3f041&GUID=&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=3D3UBmat5gcNZq5TiXH3BE62vrnklTemZ564QLAo9O7TV6B5dQmGRpTvrquXpa2NZSObdybmgqmSw9wIgJDolMVllTBdASl6&TARGET=$SM$https%3a%2f%2fpartner%2ehpe%2ecom%2fgroup%2finternal'
    current_url = driver.current_url

    while (time.time()-start_time)<=timeout: #check for internal login url for 20min
        time.sleep(1)
        try:
            current_url = driver.current_url
        except UnexpectedAlertPresentException:
            time.sleep(10)
            alert = Alert(driver)
            alert_text = alert.text
            print('\nINTERNAL LOGIN ALERT:',alert_text,'\n')
            alert.accept()
            break
    # print('^^^^^^^^^^^^^^^^^^')
    if (time.time()-start_time)>timeout: #if the extension doesn't finish its run in 20min, exit the function
        print('\nEXTENSION ERROR\n')
        driver.quit()
        return

    try: #to prevent NoAlerException that occurs during the HPE Employee Login
        alert = Alert(driver)
        alert_text = alert.text
        alert.accept()

    except NoAlertPresentException:
        pass

    wait.until(EC.element_to_be_clickable((By.ID, 'p_p_id_com_liferay_login_web_portlet_LoginPortlet_'))).click()
    authenticate_with_certificate('BOT DEC-D001a')
    extension_wait = WebDriverWait(driver,180,poll_frequency=1)

    try:
        extension_wait.until(EC.alert_is_present())  # Wait for the alert to be present
        alert = Alert(driver)
        alert_text = alert.text
        print('\nCOMPLETION ALERT:',alert_text,'\n')
        alert.accept()
        driver.quit()
        # Handle the alert based on the alert_text
    except NoAlertPresentException:
        print('\nNO ALERT FOR 3 MINUTES\n')
        driver.quit()

def prp_external(url, driver, wait):
    driver.get(url)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get('https://digital-planning-hub.its.hpecorp.net/User/Login.aspx')
    time.sleep(2)
    driver.get('https://digital-planning-hub.its.hpecorp.net/User/Login.aspx')
    wait.until(EC.element_to_be_clickable((By.ID, 'details-button'))).click()
    wait.until(EC.element_to_be_clickable((By.ID, 'proceed-link'))).click()
    time.sleep(5)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1200)
    driver.quit()


def run_mod():
    internal_url = r'https://partner.hpe.com/group/internal'
    external_url = 'https://partner.hpe.com'
    extensions = ['D:\\UAT\\Chrome Extensions\\Demo Account Validation_APJ',
        'D:\\UAT\\Chrome Extensions\\Demo Account Validation_AMS','D:\\UAT\\Chrome Extensions\\Demo Account Validation_EMEA']

    for ext in extensions:
        options = webdriver.ChromeOptions()
        print(ext)
        options.add_argument("load-extension="+ext)
        driver = webdriver.Chrome(executable_path="Webdrivers\\chromedriver.exe", chrome_options=options)
        driver.maximize_window()
        wait = WebDriverWait(driver,30,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException, TimeoutException])
        
        t1_external = threading.Thread(target=prp_external, args=(external_url, driver, wait))
        t2_internal = threading.Thread(target=prp_internal, args=(internal_url, driver, wait))
        t1_external.start()
        t2_internal.start()
        t1_external.join()
        t2_internal.join()

run_mod()
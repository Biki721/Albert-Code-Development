import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementNotVisibleException, ElementNotSelectableException, TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException


def internal_login(driver, wait):
    driver.get("https://partner.hpe.com/group/internal")
    wait.until(EC.element_to_be_clickable((By.ID, 'p_p_id_com_liferay_login_web_portlet_LoginPortlet_'))).click()
    print('------------')


def select_certi(driver, wait):
    time.sleep(5)
    try:
        # Wait for the alert to appear
        print('!!!!!!!!!!!!!!!!')
        wait.until(EC.alert_is_present())
        print('..........')
        # Switch to the alert
        alert = driver.switch_to.alert
        
        # Get the text of the alert message
        alert_text = alert.text
        print(alert_text)

        # Check if the desired option is available in the alert message
        if "BOT DEC-D001a" in alert_text:
            # Split the alert message by line breaks
            lines = alert_text.split("\n")
            
            # Search for the desired option and remember its index
            option_index = None
            for i, line in enumerate(lines):
                if "BOT DEC-D001a" in line:
                    option_index = i
                    break

            # If the desired option is found, select it
            if option_index is not None:
                # Press TAB to move focus to the first option
                for _ in range(option_index + 1):
                    alert.send_keys(Keys.TAB)
                # Press ENTER to select the desired option
                alert.send_keys(Keys.ENTER)
            else:
                # Handle the case when the desired option is not found
                # You can perform alternative actions or raise an exception here
                raise Exception("Desired option not found in the alert message")

        else:
            # Handle the case when the desired option is not found
            # You can perform alternative actions or raise an exception here
            raise Exception("Desired option not found in the alert message")

        # Accept the alert after selecting the option
        alert.accept()

    except:
        # Handle the case when the alert does not appear within the specified timeout
        # You can perform alternative actions or raise an exception here
        raise Exception("Alert did not appear within the specified timeout")


def run_mod():
    driver = webdriver.Chrome(executable_path="Webdrivers\\chromedriver.exe")
    driver.maximize_window()
    wait = WebDriverWait(driver,10,poll_frequency=1,ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException, StaleElementReferenceException])
    t1_login = threading.Thread(target=internal_login, args=(driver, wait))
    t2_certi = threading.Thread(target=select_certi, args=(driver, wait))
    t1_login.start()
    t2_certi.start()
    t1_login.join()
    t2_certi.join()

run_mod()
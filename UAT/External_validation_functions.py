import pandas as pd
import work 
import openpyxl
from inscriptis import get_text
from bs4 import BeautifulSoup
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def _has_error_text(text_content, Errormsg):
    found_text = False
    for msg in Errormsg:
        if msg in text_content:
            print(f"❌ Found error message: {msg}")
            found_text = True
            break
    return found_text

def check_seismic_login(driver, seis_login_link, wait, xpathlist, user, password):
    page = driver
    print("🔐 Logging into Seismic...")
    # ✅ Change to 'load' instead of 'networkidle'
    page.goto(seis_login_link, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_load_state("load", timeout=1200000)
    
    page.locator('xpath=//*[@id="container"]/div/div[2]/div/div[1]/div/div[1]/div/main/div[2]/div[1]/ul/li[2]/button').click()
    page.locator(f"xpath={xpathlist[1][2]}").fill(user)
    page.locator(f"xpath={xpathlist[1][3]}").click()
    page.locator(f"xpath={xpathlist[1][4]}").fill(password)
    page.locator(f"xpath={xpathlist[1][5]}").click()
    
    try:
        page.wait_for_load_state("load", timeout=1200000)
        time.sleep(1)
    except Exception:
        pass
    
    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click()
    except Exception:
        pass
    
    print("✅ Seismic login complete")


def check_seismic_error(driver, wait, xpathlist, seislink, Errormsg):
    page = driver
    
    # ✅ CRITICAL: Use 30 second timeout, not 180!
    try:
        page.goto(seislink, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

        # ✅ Wait for page to fully stabilize
        page.wait_for_load_state("load", timeout=1200000)

        # Step 3: Wait for JS redirect chain to complete
        page.wait_for_function("""
            () => {
                // Wait for Seismic content frame or final redirect
                return document.readyState === 'complete' && 
                       !document.querySelector('.loading, .spinner') &&
                       window.location.href.includes('Content/');
            }
        """, timeout=15000)
        
        # Step 4: Network stabilization (Seismic makes late AJAX calls)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except:
            print("   ⚠ Network still active, waiting 3s...")
            time.sleep(3)
        
        # ✅ Additional wait for any JavaScript redirects
        time.sleep(1.5)
    except Exception as e:
        print(f"⚠ Timeout (150s) - Trying domcontentloaded...")
        try:
            page.goto(seislink, wait_until="domcontentloaded", timeout=1200000)  # 15 sec
            time.sleep(20)
        except Exception as e2:
            print(f"❌ Complete failure: {str(e2)[:50]}")
            return True  # Mark as error
    
    try: 
        page.locator(f"xpath={xpathlist[1][1]}").click(timeout=3000)
    except Exception:
        pass
    
    # ✅ Now safe to get content
    try:
        page_content = page.content()
    except Exception as e:
        print(f"❌ Content retrieval failed: {str(e)[:50]}")
        return True
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    
    return _has_error_text(text_content, Errormsg)


def check_psnow_login(driver, errlink_psnow, wait, xpathlist, user, password):
    page = driver
    print("🔐 Logging into PSnow...")
    # ✅ Change to 'load'
    page.goto(errlink_psnow, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

    # ✅ Wait for page to fully stabilize
    page.wait_for_load_state("load", timeout=1200000)
    
    # ✅ Additional wait for any JavaScript redirects
    time.sleep(1.5)
    
    try:
        page.locator(f"xpath={xpathlist[5][1]}").click()
        page.locator(f"xpath={xpathlist[5][2]}").fill(user)
        page.locator(f"xpath={xpathlist[5][3]}").click()
        page.locator(f"xpath={xpathlist[5][4]}").fill(password)
        page.locator(f"xpath={xpathlist[5][5]}").click()
    except Exception as e:
        print(f"Login error: {str(e)[:50]}")
    
    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click()
    except Exception:
        pass
    
    print("✅ PSnow login complete")


def check_psnow_error(driver, errlink_psnow, wait, xpathlist, Errormsg):
    page = driver
    
    # ✅ 30 second timeout
    try:
        page.goto(errlink_psnow, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

        # ✅ Wait for page to fully stabilize
        page.wait_for_load_state("load", timeout=1200000)
        
        # ✅ Additional wait for any JavaScript redirects
        time.sleep(1.5)
    except Exception as e:
        print(f"⚠ Timeout (150s) - Trying domcontentloaded...")
        try:
            page.goto(errlink_psnow, wait_until="domcontentloaded", timeout=1200000)
            time.sleep(20)
        except Exception as e2:
            print(f"❌ Complete failure: {str(e2)[:50]}")
            return True
    
    try:
        page.locator(f"xpath={xpathlist[5][1]}").click(timeout=3000)
    except Exception:
        pass
    
    try:
        page.locator(f"xpath={xpathlist[5][6]}").click(timeout=3000)
    except Exception:
        pass
    
    try:
        page.locator(f"xpath={xpathlist[5][7]}").click(timeout=3000)
    except Exception:
        pass
    
    # ✅ Now safe to get content
    try:
        page_content = page.content()
    except Exception as e:
        print(f"❌ Content retrieval failed: {str(e)[:50]}")
        return True
    
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    
    return _has_error_text(text_content, Errormsg)


def check_learning_login(driver, url_hpelearn, wait, xpathlist, user, password):
    page = driver
    print("🔐 Logging into HPE Learning...")
    # ✅ Change to 'load'
    page.goto(url_hpelearn, wait_until="load", timeout=30000)
    
    page.locator(f"xpath={xpathlist[3][1]}").click()
    page.locator(f"xpath={xpathlist[3][2]}").fill(user)
    page.locator(f"xpath={xpathlist[3][3]}").click()
    page.locator(f"xpath={xpathlist[3][4]}").fill(password)
    page.locator(f"xpath={xpathlist[3][5]}").click()
    
    print("✅ HPE Learning login complete")


# def check_learning_error(driver, url_hpelearn, Errormsg):
#     page = driver
    
#     # ✅ 30 second timeout
#     try:
#         page.goto(url_hpelearn, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

#         # ✅ Wait for page to fully stabilize
#         page.wait_for_load_state("load", timeout=1200000)
        
#         # ✅ Additional wait for any JavaScript redirects
#         time.sleep(1.5)
#     except Exception as e:
#         print(f"⚠ Timeout (150s) - Trying domcontentloaded...")
#         try:
#             page.goto(url_hpelearn, wait_until="domcontentloaded", timeout=1200000)
#             time.sleep(20)
#         except Exception as e2:
#             print(f"❌ Complete failure: {str(e2)[:50]}")
#             return True
    
#     # ✅ Now safe to get content
#     try:
#         page_content = page.content()
#     except Exception as e:
#         print(f"❌ Content retrieval failed: {str(e)[:50]}")
#         return True
#     soup = BeautifulSoup(page_content, 'html.parser')
#     text_content = soup.get_text()
    
#     Errormsg = work.doc_reader("Externallink_Error_Message.docx")
#     Errormsg = [s.strip() for s in Errormsg if s != '']
    
#     return _has_error_text(text_content, Errormsg)

def check_learning_error(driver, url_hpelearn, Errormsg):
    page = driver
    
    try:
        page.goto(url_hpelearn, wait_until="domcontentloaded", timeout=35000)
        page.wait_for_load_state("load", timeout=20000)
        
        # ✅ HPE TECH PRO SPECIFIC - Waits for membership form to load
        page.wait_for_function("""
            () => {
                return document.readyState === 'complete' &&
                       document.querySelector('#form1') &&  // Main form exists
                       document.querySelector('.hpe-my-learning') &&  // HPE Learning class
                       document.querySelector('[id*="ContentPlaceHolder"]') &&  // ASP.NET content
                       !document.querySelector('.loading, .spinner');  // No loading states
            }
        """, timeout=15000)
        
        time.sleep(40)  # Final buffer for JS
        
    except Exception as e:
        print(f"⚠ HPE Learning load failed: {str(e)[:50]}")
        return True
    
    # Safe content extraction
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')
    text_content = soup.get_text()
    
    return _has_error_text(text_content, Errormsg)

def check_vs_login(driver, url_VS, wait, xpathlist, user, password):
    page = driver
    print("🔐 Logging into VShow...")
    # ✅ Change to 'load'
    page.goto(url_VS, wait_until="load", timeout=30000)
    
    page.locator(f"xpath={xpathlist[2][2]}").fill(user)
    page.locator(f"xpath={xpathlist[2][3]}").click()
    page.locator(f"xpath={xpathlist[2][4]}").fill(password)
    page.locator(f"xpath={xpathlist[2][5]}").click()
    
    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click()
    except Exception:
        pass
    
    print("✅ VShow login complete")


def check_vs_error(driver, url_VS, Errormsg):
    page = driver
    
    # ✅ 30 second timeout
    try:
        page.goto(url_VS, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

        # ✅ Wait for page to fully stabilize
        page.wait_for_load_state("load", timeout=1200000)
        
        # ✅ Additional wait for any JavaScript redirects
        time.sleep(30)
    except Exception as e:
        print(f"⚠ Timeout (150s) - Trying domcontentloaded...")
        try:
            page.goto(url_VS, wait_until="domcontentloaded", timeout=1200000)
            time.sleep(20)
        except Exception as e2:
            print(f"❌ Complete failure: {str(e2)[:50]}")
            return True
    
    # ✅ Now safe to get content
    try:
        page_content = page.content()
    except Exception as e:
        print(f"❌ Content retrieval failed: {str(e)[:50]}")
        return True
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    
    return _has_error_text(text_content, Errormsg)


def check_certification_error(driver, url_certification, Errormsg):
    page = driver
    
    # ✅ 30 second timeout
    try:
        page.goto(url_certification, wait_until="domcontentloaded", timeout=30000)  # 30 seconds

        # ✅ Wait for page to fully stabilize
        page.wait_for_load_state("load", timeout=1200000)
        
        # ✅ Additional wait for any JavaScript redirects
        time.sleep(30)
    except Exception as e:
        print(f"⚠ Timeout (150s) - Trying domcontentloaded...")
        try:
            page.goto(url_certification, wait_until="domcontentloaded", timeout=1200000)
            time.sleep(35)
        except Exception as e2:
            print(f"❌ Complete failure: {str(e2)[:50]}")
            return True
    
    # ✅ Now safe to get content
    try:
        page_content = page.content()
    except Exception as e:
        print(f"❌ Content retrieval failed: {str(e)[:50]}")
        return True
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text()
    
    return _has_error_text(text_content, Errormsg)
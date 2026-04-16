"""
country_manager.py - Centralized country selection management with decorator

This module provides utilities to ensure country selection persists across
all modules during automation. Use the @ensure_country decorator on any
method that navigates pages.
"""

import time
import functools
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class CountryManager:
    """
    Manages country selection state and verification across the session.
    Thread-safe for concurrent execution.
    """
    
    def __init__(self, prp_instance):
        """
        Initialize CountryManager with a PRP instance.
        
        Args:
            prp_instance: Instance of PRP class with page, country, etc.
        """
        self.prp = prp_instance
        self.page = prp_instance.page
        self.target_country = prp_instance.country
        self.last_check_time = 0
        self.navigation_count = 0
        self.check_interval = 300  # Check every 5 minutes (300 seconds)
        self.nav_check_frequency = 10  # Check every N navigations
        
    
    def country_similarity(self, a: str, b: str):
        """Calculate similarity between two country names."""
        if not a or not b:
            return 0

        a = a.lower()
        b = b.lower()

        # Token-based similarity
        a_tokens = set(a.replace("(", " ").replace(")", " ").split())
        b_tokens = set(b.replace("(", " ").replace(")", " ").split())

        token_overlap = len(a_tokens & b_tokens)
        token_total = max(len(a_tokens), 1)
        token_score = token_overlap / token_total

        # Character similarity
        matches = sum(1 for ch in a if ch in b)
        char_score = matches / max(len(a), 1)

        return (token_score * 0.6) + (char_score * 0.4)
    
    
    def get_current_country(self):
        """
        Get the currently selected country from the portal.
        
        Returns:
            str: Current country name or empty string if cannot detect
        """
        page = self.page
        
        try:
            # Open eyeball
            eyeball = page.query_selector("#MHMG-usereye")
            if eyeball:
                eyeball.click()
                time.sleep(2)
            
            # Get current country
            selector = (
                '#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet '
                '> div > div.portlet-content-container > div > div.MHMGuserdescrp '
                '> div > div.MHMGcountryname'
            )
            country_element = page.wait_for_selector(selector, timeout=10000)
            current_country = country_element.inner_text().strip() if country_element else ""
            
            # Close eyeball
            try:
                page.keyboard.press("Escape")
                time.sleep(1)
            except:
                try:
                    if eyeball:
                        eyeball.click()
                        time.sleep(1)
                except:
                    pass
            
            return current_country
            
        except Exception as e:
            print(f"⚠️ Could not detect current country: {e}")
            # Try to close eyeball anyway
            try:
                page.keyboard.press("Escape")
            except:
                pass
            return ""
    
    
    def verify_and_fix_country(self, force=False):
        """
        Verify country selection and fix if needed.
        
        Args:
            force (bool): Force check even if recent check was done
            
        Returns:
            bool: True if country is correct, False if fix failed
        """
        current_time = time.time()
        
        # Skip if recently checked (unless forced)
        if not force and (current_time - self.last_check_time) < self.check_interval:
            return True
        
        print(f"\n🔍 Verifying country selection...")
        current_country = self.get_current_country()
        
        if not current_country:
            print("⚠️ Could not verify country")
            return False
        
        # Check if correct
        similarity = self.country_similarity(current_country, self.target_country)
        
        if similarity >= 0.5:
            print(f"✅ Country verified: '{current_country}'")
            self.last_check_time = current_time
            return True
        
        # Country is wrong, fix it
        print(f"⚠️ Country mismatch! Current: '{current_country}', Expected: '{self.target_country}'")
        print(f"🔧 Correcting country selection...")
        
        return self._fix_country()
    
    
    def _fix_country(self):
        """
        Fix country selection by switching to correct country.
        
        Returns:
            bool: True if successful, False otherwise
        """
        page = self.page
        
        try:
            # Close any overlays first
            self._close_overlay()
            time.sleep(2)
            
            # Open eyeball
            eyeball = page.wait_for_selector("#MHMG-usereye", state="visible", timeout=30000)
            if eyeball:
                eyeball.click()
                time.sleep(3)
            
            # Open country dropdown
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", 
                                            state="visible", timeout=15000)
            if loc_btn:
                loc_btn.click()
                time.sleep(2)
            
            # Wait for country list
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", 
                                  state="visible", timeout=20000)
            time.sleep(2)
            
            # Find and click correct country
            options = page.query_selector_all("ul#MHMGBRcountries li.locationsBRlist")
            
            best_score = 0
            best_option = None
            best_name = ""
            
            for opt in options:
                try:
                    cname = opt.get_attribute("countryname") or opt.inner_text().strip()
                except:
                    continue
                
                score = self.country_similarity(self.target_country, cname)
                
                if score > best_score:
                    best_score = score
                    best_option = opt
                    best_name = cname
            
            if best_score >= 0.30 and best_option:
                # Click country
                try:
                    best_option.click()
                except Exception:
                    page.evaluate("(el)=>el.click()", best_option)
                
                print(f"🌐 Selected country: '{best_name}' (match score: {best_score:.2f})")
                time.sleep(2)
                
                # Click BR container to confirm
                br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div", 
                                                     state="visible", timeout=15000)
                if br_container:
                    br_container.click()
                    print("⏳ Waiting for country change to persist...")
                    
                    # Critical: Wait for page reload and session update
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                        page.wait_for_load_state("networkidle", timeout=60000)
                    except Exception as e:
                        print(f"⚠️ Load state warning: {e}")
                    
                    # Additional wait for session persistence
                    time.sleep(5)
                    print("✅ Country change completed")
                    
                    self.last_check_time = time.time()
                    return True
            else:
                print(f"❌ No matching country found for '{self.target_country}'")
                return False
                
        except Exception as e:
            print(f"❌ Country fix failed: {e}")
            return False
    
    
    def _close_overlay(self):
        """Close notification overlay if present."""
        page = self.page
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5000)
            if overlay and overlay.is_visible():
                print("⚠️ Closing overlay...")
                try:
                    close_btn = page.locator("#closemsg")
                    close_btn.wait_for(state="visible", timeout=5000)
                    close_btn.click()
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=10000)
                except:
                    pass
        except PlaywrightTimeoutError:
            pass
        except Exception:
            pass


# ============================================================================
# DECORATOR FUNCTIONS
# ============================================================================

def ensure_country(check_frequency=10):
    """
    Decorator to ensure country is correct before/after method execution.
    
    Usage:
        @ensure_country(check_frequency=10)
        def my_navigation_method(self, url):
            # Your code here
            pass
    
    Args:
        check_frequency (int): Check country every N method calls
    
    The decorated method's class must have:
        - self.country_manager (CountryManager instance)
        - self.page (Playwright page object)
    """
    def decorator(func):
        func._call_count = 0
        
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Increment call counter
            func._call_count += 1
            
            # Check if country manager exists
            if not hasattr(self, 'country_manager'):
                print("⚠️ Warning: No country_manager found, skipping country check")
                return func(self, *args, **kwargs)
            
            # Periodic check based on frequency
            force_check = (func._call_count % check_frequency) == 0
            
            if force_check:
                print(f"🔄 Periodic country check (call #{func._call_count})...")
                self.country_manager.verify_and_fix_country(force=True)
            
            # Execute the original function
            result = func(self, *args, **kwargs)
            
            return result
        
        return wrapper
    return decorator


def ensure_country_for_delayed(func):
    """
    Special decorator for delayed loading links.
    Always checks country before and after the operation.
    
    Usage:
        @ensure_country_for_delayed
        def integrate(self, site):
            # Your code here
            pass
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check if this is a delayed loading link
        is_delayed = False
        if args:
            site = args[0] if isinstance(args[0], str) else None
            if site and hasattr(self, 'delayed_loading_links'):
                is_delayed = (site in self.delayed_loading_links or 
                             site.strip() in self.delayed_loading_links)
        
        # For delayed links, always verify country
        if is_delayed and hasattr(self, 'country_manager'):
            print(f"🔄 Pre-check for delayed loading link...")
            self.country_manager.verify_and_fix_country(force=True)
        
        # Execute the original function
        result = func(self, *args, **kwargs)
        
        # Verify again after delayed loading
        if is_delayed and hasattr(self, 'country_manager'):
            print(f"🔄 Post-check for delayed loading link...")
            self.country_manager.verify_and_fix_country(force=True)
        
        return result
    
    return wrapper


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def initialize_country_manager(prp_instance):
    """
    Initialize and attach CountryManager to a PRP instance.
    
    Usage:
        from country_manager import initialize_country_manager
        
        prp = PRP(...)
        initialize_country_manager(prp)
    
    Args:
        prp_instance: Instance of PRP class
    """
    prp_instance.country_manager = CountryManager(prp_instance)
    print("✅ CountryManager initialized")
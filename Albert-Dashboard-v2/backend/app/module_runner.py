"""
Unified module runner for automation modules
Provides a consistent interface to run all automation modules
"""
import sys
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import traceback
import importlib.util
from urllib import request

from .config import settings
from .models import (
    AutomationRequest, AutomationMode, DomainType, 
    ModuleType, AdhocType, JobStatus
)


# Add UAT directory to Python path
sys.path.insert(0, str(settings.MODULES_DIR))


class ModuleRunner:
    """
    Executes automation modules with unified interface
    """
    
    # Map domain types to module classes
    # Only PRP is supported in v2; MarketingPro and Competitor have been removed
    DOMAIN_MODULES = {
        DomainType.PRP: ("modulepagetree_phase4", "PRP"),
    }
    
    # Map module types to module classes
    VALIDATION_MODULES = {
        ModuleType.BROKEN_LINKS: ("modulebrokenlinks_phase4", "PRP"),
        ModuleType.TRANSLATION_EMPTY: ("moduletransnempty_phase4", "PRP"),
        ModuleType.NEW_TAB: ("modulenewtab_phase4", "PRP"),
        ModuleType.T_VARIABLE: ("moduletvar_phase4", "PRP"),
        ModuleType.EXTERNAL_LINKS: ("Module_externallinks_validation", "PRP"),
        ModuleType.TRANSLATION_SPELLING_EMPTY: ("module_trans_spell_empt_phase4", "PRP"),
        ModuleType.SPELLING_CHECK: ("module_spell_check_phase4", "PRP"),
        ModuleType.LOGIN: ("module_login_lang", "PRP")

    }

    LOGIN_DEPENDENT_MODULES = {
        ModuleType.TRANSLATION_SPELLING_EMPTY,
        ModuleType.TRANSLATION_EMPTY
}
    
    # Map adhoc types
    ADHOC_MODULES = {
        AdhocType.WORD_SEARCH: ("module_adhoc_word_search", "PRP"),
        AdhocType.URL_SEARCH: ("module_adhoc_link_search", "PRP"),
    }
    
    def __init__(self):
        self.stop_flag = False
        self._current_job_id: Optional[str] = None
        self._progress_callback: Optional[Callable] = None
    
    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self._progress_callback = callback
    
    def _update_progress(self, message: str):
        """Update progress if callback is set"""
        if self._progress_callback:
            self._progress_callback(message)
    
    def _import_module(self, module_name: str, class_name: Optional[str] = None):
        """Dynamically import module class"""
        try:
            module_path = settings.MODULES_DIR / f"{module_name}.py"
            print(f"Trying to import from: {module_path}")
            
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if class_name:
                return getattr(module, class_name)
            
            return module
        except Exception as e:
            raise ImportError(f"Failed to import {class_name} from {module_name}: {e}")
    
    def _parse_account(self, account_str: str) -> List[str]:
        """Parse account string into components"""
        # Format: email|password|region|country|language|type
        return account_str.split('|')
    
    def _run_domain_module(self, domain: DomainType, account_details: List[str]) -> Dict[str, Any]:
        """Run a domain (page tree) module"""

        print(">>> ENTERING DOMAIN MODULE")
        print(">>> CALLING setUp()")
        module_name, class_name = self.DOMAIN_MODULES[domain]
        
        self._update_progress(f"Running domain {domain.value} for account {account_details[0]}")
        
        try:
            ModuleClass = self._import_module(module_name, class_name)
            instance = ModuleClass(*account_details)
            
            instance.setUp()
            instance.scrapecall_writetrees()
            instance.tearDown()
            
            return {
                "status": "success",
                "domain": domain.value,
                "account": account_details[0]
            }
        except Exception as e:
            print("🔥 DOMAIN MODULE ERROR:", e)
            print(traceback.format_exc())
            return {
                "status": "error",
                "domain": domain.value,
                "account": account_details[0],
                "error": str(e)
            }
    
    def _run_validation_module(self, module: ModuleType, account_details: List[str]):

        if module in self.LOGIN_DEPENDENT_MODULES:
            return self._run_login_dependent_module(module, account_details)
        else:
            return self._run_standard_module(module, account_details)
        
    def _run_login_dependent_module(self, module: ModuleType, account_details: List[str]):

        module_name, class_name = self.VALIDATION_MODULES[module]

        try:
            ModuleClass = self._import_module(module_name, class_name)

            # Import login module dynamically
            login_module = self._import_module("module_login_lang", "PRP")

            # 1️⃣ Login
            login_instance = login_module(*account_details)
            login_instance.setUp()

            login_success = login_instance.login()

            if not login_success:
                login_instance.tearDown()
                raise Exception("Login failed")

            # 2️⃣ Main module reusing browser
            instance = ModuleClass(
                *account_details,
                playwright=login_instance.playwright,
                browser=login_instance.browser,
                page=login_instance.page
            )

            instance.setUp()

            if module == ModuleType.TRANSLATION_SPELLING_EMPTY:
                instance.parent()
            elif module == ModuleType.SPELLING_CHECK:
                instance.parent()  # or correct method if different

            instance.tearDown()

            return {
                "status": "success",
                "module": module.value,
                "account": account_details[0]
            }

        except Exception as e:
            return {
                "status": "error",
                "module": module.value,
                "account": account_details[0],
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _run_standard_module(self, module: ModuleType, account_details: List[str]) -> Dict[str, Any]:
        """Run a validation module"""
        module_name, class_name = self.VALIDATION_MODULES[module]
        
        self._update_progress(f"Running module {module.value} for account {account_details[0]}")
        
        try:
            ModuleClass = self._import_module(module_name, class_name)
            instance = ModuleClass(*account_details)
            
            # instance.setUp()
            
            # Call appropriate test method based on module
            if module == ModuleType.BROKEN_LINKS:
                instance.setUp()
                instance.test_load_home_page()
                instance.test_multiple_broken()
                instance.tearDown()
            elif module == ModuleType.TRANSLATION_EMPTY:
                instance.test_load_home_page()
                instance.parent()
                instance.tearDown()
            elif module == ModuleType.NEW_TAB:
                instance.test_new_tab()
                instance.tearDown()
            elif module == ModuleType.T_VARIABLE:
                instance.test_tvar_check()
                instance.tearDown()
            elif module == ModuleType.EXTERNAL_LINKS:
                instance.external_url_validation()
                instance.tearDown()
            elif module == ModuleType.TRANSLATION_SPELLING_EMPTY:
                pass
            elif module == ModuleType.SPELLING_CHECK:
                pass
            
            
            # instance.tearDown()
            
            return {
                "status": "success",
                "module": module.value,
                "account": account_details[0]
            }
        except Exception as e:
            return {
                "status": "error",
                "module": module.value,
                "account": account_details[0],
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    # def _run_validation_module(self, module: ModuleType, account_details: List[str]) -> Dict[str, Any]:
    #     """Run a validation module"""
    #     module_name, class_name = self.VALIDATION_MODULES[module]
        
    #     self._update_progress(f"Running module {module.value} for account {account_details[0]}")
        
    #     try:
    #         ModuleClass = self._import_module(module_name, class_name)
    #         instance = ModuleClass(*account_details)
            
    #         # instance.setUp()
            
    #         # Call appropriate test method based on module
    #         if module == ModuleType.BROKEN_LINKS:
    #             instance.setUp()
    #             instance.test_load_home_page()
    #             instance.test_multiple_broken()
    #             instance.tearDown()
    #         elif module == ModuleType.TRANSLATION_EMPTY:
    #             instance.test_load_home_page()
    #             instance.parent()
    #             instance.tearDown()
    #         elif module == ModuleType.NEW_TAB:
    #             instance.test_new_tab()
    #             instance.tearDown()
    #         elif module == ModuleType.T_VARIABLE:
    #             instance.test_tvar_check()
    #             instance.tearDown()
    #         elif module == ModuleType.EXTERNAL_LINKS:
    #             instance.external_url_validation()
    #             instance.tearDown()
    #         elif module == ModuleType.TRANSLATION_SPELLING_EMPTY:
    #             pass
    #         elif module == ModuleType.SPELLING_CHECK:
    #             pass
            
            
    #         # instance.tearDown()
            
    #         return {
    #             "status": "success",
    #             "module": module.value,
    #             "account": account_details[0]
    #         }
    #     except Exception as e:
    #         return {
    #             "status": "error",
    #             "module": module.value,
    #             "account": account_details[0],
    #             "error": str(e),
    #             "traceback": traceback.format_exc()
    #         }
    
    def _run_adhoc_module(self, adhoc_type: AdhocType) -> Dict[str, Any]:
        """Run an adhoc module"""

        print(">>> ENTERED _run_adhoc_module")
        print(">>> ADHOC TYPE:", adhoc_type)
        module_name, class_name = self.ADHOC_MODULES[adhoc_type]
        
        # Hardcoded account for adhoc
        account_details = [
            'bot.dec-d001a@hpe.com', 
            'Login2PRP!', 
            'NA', 
            'USA', 
            'English', 
            'T2'
        ]
        
        self._update_progress(f"Running adhoc task {adhoc_type.value}")
        
        try:
            print(">>> Importing module")
            ModuleClass = self._import_module(module_name, class_name)

            print(">>> Creating instance")
            instance = ModuleClass(*account_details)

            print(">>> Calling setUp()")
            instance.regen_tree = True 
            instance.setUp()

            print(">>> Calling parent()")
            instance.parent()

            print(">>> Calling tearDown()")
            instance.tearDown()
            
            return {
                "status": "success",
                "adhoc_type": adhoc_type.value
            }
        except Exception as e:
            print("🔥🔥🔥 ADHOC CRASH 🔥🔥🔥")
            print(traceback.format_exc())
            return {
                "status": "error",
                "adhoc_type": adhoc_type.value,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def run_automation(self, request: AutomationRequest, job_id: str) -> Dict[str, Any]:
        """
        Execute automation request
        Returns results dictionary
        """
        self._current_job_id = job_id
        self.stop_flag = False
        results = {
            "job_id": job_id,
            "started_at": datetime.utcnow().isoformat(),
            "account_results": [],
            "errors": []
        }
        
        try:
            if request.mode == AutomationMode.REGULAR:
                results.update(self._run_regular_automation(request))
            elif request.mode == AutomationMode.ADHOC:
                results.update(self._run_adhoc_automation(request))
            
            results["completed_at"] = datetime.utcnow().isoformat()
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["traceback"] = traceback.format_exc()
            results["completed_at"] = datetime.utcnow().isoformat()
        
        return results
    
    def _run_regular_automation(self, request: AutomationRequest) -> Dict[str, Any]:
        """Run regular mode automation"""
        results = {
            "mode": "regular",
            "domain_results": [],
            "module_results": []
        }
        print("ACCOUNTS:", request.accounts)
        print("DOMAINS:", request.domains)
        
        for account_str in request.accounts:
            if self.stop_flag:
                self._update_progress("Stopped by user")
                break
            
            account_details = self._parse_account(account_str)
            
            # Run domains
            for domain in request.domains:
                if self.stop_flag:
                    break

                # Skip any domains that are not supported
                if domain not in self.DOMAIN_MODULES:
                    continue

                result = self._run_domain_module(domain, account_details)
                results["domain_results"].append(result)
            
            # Run validation modules
            for module in request.modules:
                if self.stop_flag:
                    break
                
                result = self._run_validation_module(module, account_details)
                results["module_results"].append(result)
        
        # Handle SharePoint upload
        if request.sharepoint_upload and not self.stop_flag:
            try:
                self._update_progress("Aggregating reports...")

                merge_module = self._import_module("merge_upload", None)

                aggregate = getattr(merge_module, "aggregate")
                to_be_merged_folderpath = getattr(merge_module, "to_be_merged_folderpath")

                aggregate(to_be_merged_folderpath)
                results["sharepoint_uploaded"] = True
            except Exception as e:
                results["sharepoint_upload_error"] = str(e)
        
        return results
    
    def _run_adhoc_automation(self, request: AutomationRequest) -> Dict[str, Any]:
        """Run adhoc mode automation"""
        results = {
            "mode": "adhoc",
            "adhoc_results": []
        }
        
        result = self._run_adhoc_module(request.adhoc_type)
        results["adhoc_results"].append(result)
        
        return results
    
    def stop(self):
        """Stop current execution"""
        self.stop_flag = True
        self._update_progress("Stop requested...")


# Global runner instance
module_runner = ModuleRunner()

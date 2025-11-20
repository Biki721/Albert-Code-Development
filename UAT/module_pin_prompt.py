from pywinauto import Application
import time



def handle_pin_prompt(pin, max_wait_time=20):
    """
    Handle Windows Security PIN prompt with ultra-fast checking
    """
    status = False
    elapsed_time = 0
    check_interval = 0.1  # Check every 100ms for ultra-fast response
    
    print(f"🔍 Looking for Windows Security dialog (max wait: {max_wait_time}s)...")
    
    while elapsed_time < max_wait_time:
        try:
            # Try to find the Windows Security dialog
            app_prompt = Application(backend='uia').connect(title='Windows Security',
                                                            class_name='Credential Dialog Xaml Host',
                                                            control_type="Window")
            print("✅ Found Windows Security dialog")
            
            main_app_window = app_prompt.top_window()
            main_app_window.set_focus()
            
            # Type the PIN
            password_field = main_app_window.child_window(auto_id="PasswordField_0", control_type="Edit")
            password_field.type_keys(pin)
            print("🔑 PIN entered successfully")
            
            # Click OK button
            ok_button = main_app_window.child_window(title="OK", auto_id="OkButton", control_type="Button")
            ok_button.click()
            print("✅ OK button clicked")
            
            status = True
            break
            
        except Exception as e:
            elapsed_time += check_interval
            if elapsed_time < max_wait_time:
                # Only print status every 5 seconds to avoid spam (since we check every 100ms)
                if abs(elapsed_time % 5) < check_interval:
                    print(f"⏳ Dialog not found yet, waiting... ({elapsed_time:.1f}/{max_wait_time}s)")
                time.sleep(check_interval)
            else:
                print(f"⚠️ Windows Security dialog not found within {max_wait_time} seconds")
                print(f"Exception: {str(e)}")
    
    if status:
        print("✅ PIN prompt handled successfully")
    else:
        print("❌ Failed to handle PIN prompt - dialog may not have appeared")
    
    return status

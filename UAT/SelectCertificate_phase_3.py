from pywinauto import Application, findwindows, controls, uia_defines
from pywinauto.findwindows import ElementNotFoundError
import time
from subprocess import PIPE, run


class CertificateNotFoundError(Exception):
    pass


def authenticate_with_certificate(cert_name, max_wait_time=40):
    print("into certi selection")
    """
    Function to select the certificate in google chrome while accessing hpe web tools
    :param cert_name: Name of the certificate which we can obtained from Internet Options > Content > Certificates > "Your certificate" > Details > Subject > Copy the value of CN. Example: BOT FIN-CI001 --> String
    :param max_wait_time: Maximum wait time of the certificate selection window to popup --> Int
    :return: Status of the certificate selection to identify whether the action is success or failure --> Boolean 
    """
    selected = False
    window_found = False
    wait_time = max_wait_time
    while wait_time > 0:
        handle1 = findwindows.find_elements(backend="uia", visible_only=False,title='Submit Form - Google Chrome', class_name='Chrome_WidgetWin_1',control_type="Pane")
        handle2 = findwindows.find_elements(backend="uia", visible_only=False,title='Select a certificate', class_name='Chrome_WidgetWin_1',control_type="Pane")
        if len(handle1) > 0:
            handle = handle1[0]
            window_found = True
            break
        elif len(handle2) > 0:
            handle = handle2[0]
            window_found = True
            break
        else:
            wait_time -= 10
            time.sleep(10)
    print(window_found,'**********************************************')
    if window_found:
        app = Application(backend='uia').connect(handle=controls.uiawrapper.UIAWrapper(handle))
        app_window = app.top_window()
        app_window.set_focus()
        list_element = app_window.child_window(top_level_only=False, control_type='List', found_index=0)
        print('^^^^^^^^^^^^^^',list_element)
        list_element_info = list_element.wrapper_object().element_info
        cert_count = int((run(['powershell.exe',
                               '(Get-ChildItem -path Cert:\CurrentUser\My -Recurse | Where-Object { $_.Subject -like "*Hewlett Packard Enterprise*" }).Count'],
                              stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)).stdout)
        cert_row = controls.uia_controls.ListViewWrapper(list_element_info)
        for i in range(cert_count):
            selected_row = cert_row.get_selection()
            data_item = selected_row[0].descendants()[0]
            if data_item.name == cert_name:
                uia_defines.get_elem_interface(list_element_info.element, "LegacyIAccessible").DoDefaultAction()
                selected = True
                break
            else:
                time.sleep(2)
                list_element.type_keys('{DOWN}')
        if not selected:
            raise CertificateNotFoundError(f'ERROR: Certificate issued by Hewlett Packard Enterprise with the CN: "{cert_name}" not found.')
        return True
    else:
        pass
        raise ElementNotFoundError(
            f'ERROR: Unable to find the chrome certificate selection window within the maximum wait time of "{max_wait_time}" seconds.')


def handle_pin_prompt(pin, max_wait_time=120):
    status = False
    wait_time = max_wait_time
    while wait_time > 0:
        try:
            app_prompt = Application(backend='uia').connect(title='Windows Security',
                                                            class_name='Credential Dialog Xaml Host',
                                                            control_type="Window")
            main_app_window = app_prompt.top_window()
            main_app_window.set_focus()
            main_app_window.child_window(auto_id="PasswordField_0", control_type="Edit").type_keys(pin)
            main_app_window.child_window(title="OK", auto_id="OkButton", control_type="Button").click()
            status = True
            break
        except:
            wait_time -= 10
            time.sleep(10)
    # if not status:
    #     raise ElementNotFoundError(
    #         f'ERROR: Unable to find the security pin window within the maximum wait time of "{max_wait_time}" seconds.')
    return True



import pandas as pd

df = pd.read_excel('WA Reports\Aggregated Report.xlsx')

def filter(col_header, error_desc):
    fin_df = df
    fin_df = fin_df[fin_df[col_header]!=error_desc]
    return fin_df

# df = df[df['Description']!="['As a Service']"]
# df = df[df['Description']!="['fors']"]
# df = df[df['Description']!="['Copyright Development L P']"]
# df = df[df['Description']!="['null', 'User is inactive PRP Please contact adminstration for activation', 'ToolsCertification Learning resourcesTraining materialsNews and EventsSocial Media and Marketing tools', 'Caps Lock is on', 'Thank you for choosing to partner with All users must sign up for access to the Please select your business relationship type below to register and connect to all the resources you need', 'login hook new user_cpp_siteminder_login_hook', 'Select your business relationship', 'oops you do not have an account on this system_cpp_siteminder_login_hook', 'Supplier', 'The gives partners direct access to all the critical business tools and information they need to do business with', 'Email', 'LanguageEnglishSelect oneEnglish中文한국어EspañolРусский中文PortuguêsDeutschTürkçeItalianoFrançaisBahasa Indonesia日本語']"]
# df = df[df['Description']!="['null', 'User is inactive PRP Please contact adminstration for activation', 'ToolsCertification Learning resourcesTraining materialsNews and EventsSocial Media and Marketing tools', 'Caps Lock is on', 'Thank you for choosing to partner with All users must sign up for access to the Please select your business relationship type below to register and connect to all the resources you need', 'login hook new user_cpp_siteminder_login_hook', 'Select your business relationship', 'oops you do not have an account on this system_cpp_siteminder_login_hook', 'Supplier', 'The gives partners direct access to all the critical business tools and information they need to do business with', 'Email']"]
# df = df[df['Description']!="['ATP Administrator Foundati V']"]
# df = df[df['Description']!="['PPU Guide']"]

fp_errors = ["['As a Service']","['fors']","['ATP Administrator Foundati V']","['PPU Guide']","['Copyright Development L P']","['for']","['ATP Administrator Foundatis']"]

for fp in fp_errors:
    df = filter('Description', fp)

df['Category'] = df['Category'].replace('Ad hoc','Translation Error')

df.reset_index(drop=True, inplace=True)
df['Issue ID'] = range(len(df))

df.to_excel('Aggregated Report.xlsx', index=False)
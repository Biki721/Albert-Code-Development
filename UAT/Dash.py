import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from demo_accounts import demo_accounts
from flask_app import app
from render_table import layout
from modulepagetree import PRP
from marketing_pro_page_tree import PRP as MarketingPro
from competitor_page_tree import PRP as Competitor
from modulebrokenlinks_phase3 import PRP as Broken_Links
from moduletransnempty_phase3 import PRP as Translation_and_Empty_Page
from modulenewtab_phase3 import PRP as New_Tab
from moduletvar_phase3 import PRP as T_variable
from dash.exceptions import PreventUpdate
from dash import dash_table
from datetime import date
import datetime
import threading
from apscheduler.schedulers.background import BackgroundScheduler
import os
from merge_upload import to_be_uploaded_filepath, to_be_merged_folderpath, aggregate, upload
from render_word_search_table import layout_2
from ad_hoc_pgtree import PRP as Adhoc_page_tree
from adhoc_internal_login import PRP as Adhoc_internal_login
from dash import callback_context

global stop_crawler
stop_crawler = False



scheduler = BackgroundScheduler()

def initialize_scheduler():
    if not scheduler.running:
        scheduler.start()

initialize_scheduler()

# File path to store the running status of Albert
albert_status_file = 'albert_status.txt'

# Function to write the status to the file
def write_status(status):
    with open(albert_status_file, 'w') as file:
        file.write(status)

# Function to read the status from the file
def read_status():
    if os.path.exists(albert_status_file):
        with open(albert_status_file, 'r') as file:
            return file.read().strip()
    return None

# Set up Dash
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/')

dash_app.layout = html.Div([
    html.Div(
        children=[
            html.Div(className='logo', children=[
                html.Img(src='assets/logo.png')
            ]),
            html.H1('Albert Interface', className='center-div'),
            html.Button([
                    dcc.Markdown('''
                    <div class="sign">
                        <svg viewBox="0 0 512 512">
                            <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z">
                            </path>
                        </svg>
                    </div>
                    ''', dangerously_allow_html=True),
                    html.Div('Logout', className='text')
                ], id='logout-button',className='Btn'),
        ],
    ), 
    dcc.Tabs([
        dcc.Tab(label='Dashboard', children=[
            html.Div([
                # html.H1('Albert Interface', className='center-div'),

                html.Div([
                    html.Br(),
                    html.Br(),
                    dcc.RadioItems(
                        id='mode-selection',
                        options=[
                            {'label': 'Regular', 'value': 'REG'},
                            {'label': 'Adhoc', 'value': 'ADH'}
                        ],
                        value='REG',
                        labelStyle={'display': 'inline-block'}
                    )
                ], className='radio-button'),
                html.Br(),


                html.Div(id='regular-dropdowns', children=[
                    html.Div([
                        html.Div([
                            html.H3('Language'),
                            dcc.Dropdown(
                                id='language-dropdown',
                                options=[{'label': language, 'value': language} for language in demo_accounts.keys()],
                                placeholder="Select a language",
                                multi=True,
                                searchable=True,
                                className='dropdown',
                            ),
                        ], className='column'),

                        html.Div([
                            html.H3('Demo Accounts'),
                            dcc.Dropdown(
                                id='demo-account-dropdown',
                                placeholder="Select demo accounts",
                                multi=True,
                                searchable=True,
                                className='dropdown',

                            ),
                        ], className='column'),
                    ], className='row'),

                    html.Div([
                        html.Div([
                            html.H3('Domains'),
                            dcc.Dropdown(
                                id='page-tree-dropdown',
                                options=[{'label': i, 'value': i} for i in ['PRP', 'MarketingPro', 'Competitor']],
                                placeholder="Select Domain",
                                multi=True,
                                searchable=True,
                                className='dropdown',
                            ),
                        ], className='column'),

                        html.Div([
                            html.H3('Modules'),
                            dcc.Dropdown(
                                id='module-dropdown',
                                options=[{'label': i, 'value': i} for i in ['Broken_Links', 'Translation_and_Empty_Page', 'New_Tab', 'T_variable']],
                                placeholder="Select modules",
                                multi=True,
                                searchable=True,
                                className='dropdown',
                            ),
                        ], className='column'),
                    ], className='row'),

                    dcc.Location(id='url', refresh=True),
                ]),
                html.Div(id='adhoc-dropdowns', children=[
                    html.Div([

                        html.Div([
                            html.H3('Adhocs'),
                            dcc.Dropdown(
                                id='adhoc-dropdown',
                                options=[{'label': i, 'value': i} for i in ['Adhoc Word Search', 'Adhoc URL Search']],
                                placeholder="Select an option",
                                searchable=False,
                                className='dropdown',
                            ),

                        ],className='column'),

                        
                        
                    html.Div([layout_2],className='column',id='layout-2-container',style={'display': 'none'}) , 
                 ],className='row')   
                ],style={'display': 'none'}),

                

                # html.Button('Logout', id='logout-button'),
                html.Div(id='page-content'),

                html.Div([

                    html.Div([
                        html.H3('SharePoint Upload'),
                        dcc.Dropdown(
                            id='sharepoint-upload-dropdown',
                            options=[{'label': i, 'value': i} for i in ['Yes', 'No']],
                            placeholder="Select Yes or No",
                            searchable=False,
                            className='dropdown',
                        ),
                    ], className='column'),
                    html.Br(),
                    html.Br(),

                    html.Div([
                        html.H3('Schedule Date',id='schedule'),
                        dcc.DatePickerSingle(
                        id='date-picker-single',
                        month_format='MMM Do, YY',
                        placeholder='MMM Do, YY',
                        date=datetime.date.today(),
                        # calendar_orientation='vertical',
                    ),
                    ], className='column'),

                    html.Div([
                        html.H3('Run Time'),
                        dcc.Input(id='scheduled-time-input', type='time', value='00:00'),  
                    ], className='column'),
                    
                ], className='row'),
                html.Br(),
                html.Br(),
                html.Div([
                    html.Div([
                        html.Button('Run Albert', id='run-crawler-button'),
                    ], className='column'),

                    html.Div([
                        html.Button('Stop Albert', id='stop-crawler-button'),
                    ], className='column'),

                ], className='row'),

                html.Br(),
                html.Br(),
                html.Div(id='crawler-output'),
                html.Div(id='stop-output'),
                html.Div(id='adhoc-output'),
                
            ])
        ],id='tab1',className='tab-content'),

        dcc.Tab(label='Excel Table', children=[
            html.Br(),
            layout
        ],id='tab2',className='tab-content'),
    ],className='tabs')
], className='popup')

@dash_app.callback(
    [Output('layout-2-container', 'style'),
    Output('adhoc-dropdown', 'style')],
    [Input('adhoc-dropdown', 'value')]
)
def toggle_adhoc_layout(value):
    dropdown_style = {'width': '80%'}  # Set default width for the dropdown
    adhoc_dropdowns_style = {'display': 'none'}  # Set default style for the container

    if value == 'Adhoc Word Search':
        adhoc_dropdowns_style = {'display': 'block'}  # Show the container
    else:
        adhoc_dropdowns_style = {'display': 'none'}  # Hide the container

    return adhoc_dropdowns_style, dropdown_style

@dash_app.callback(
    [Output('regular-dropdowns', 'style'),
     Output('adhoc-dropdowns', 'style')],
    [Input('mode-selection', 'value')]
)
def toggle_dropdowns(mode):
    if mode == 'REG':
        return {'display': 'block'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'display': 'block'}




@dash_app.callback(
    Output('url', 'pathname'),
    [Input('logout-button', 'n_clicks')]
)
def logout(n_clicks):
    if n_clicks is not None:
        return '/dashboard/logout'

crawler_results = []

@dash_app.callback(
    [Output('demo-account-dropdown', 'options'),
     Output('crawler-output', 'children')],
    [Input('language-dropdown', 'value'),
     
     Input('run-crawler-button', 'n_clicks'),
     Input('scheduled-time-input', 'value'),
     Input('date-picker-single', 'date'),
     Input('sharepoint-upload-dropdown', 'value')],
    [State('demo-account-dropdown', 'value'),
     State('page-tree-dropdown', 'value'),
     State('module-dropdown', 'value')]
)
def update_demo_account_and_run_web_crawler(selected_languages, n_clicks, selected_time, selected_date, sharepoint_upload, selected_accounts, selected_page_trees, selected_modules):
    # Your callback function code here

    # Initialize the outputs
    demo_account_options = []
    global crawler_results
    
    # Check if languages are selected and update demo account options
    if selected_languages is not None:
        accounts = []
        for language in selected_languages:
            accounts.extend(demo_accounts.get(language, []))
        demo_account_options = [{'label': account[0], 'value': '|'.join(account)} for account in accounts]


    print(f"Selected time: {selected_time}")
    print(f"Selected date: {selected_date}")
    
    # Check if button is clicked, selected accounts are available, and a Page Tree is selected
    if n_clicks and selected_accounts and selected_page_trees and selected_modules and selected_time and selected_date:
        # Schedule the job for the selected time
        # Schedule the job for the selected date and time
        selected_date_and_time = datetime.datetime.strptime(selected_date + " " + selected_time, "%Y-%m-%d %H:%M")
        scheduler.add_job(run_web_crawler, 'date', run_date=selected_date_and_time, args=[selected_accounts, selected_page_trees, selected_modules, sharepoint_upload],id='web_crawler_job')
        write_status(f"{selected_date} {selected_time}: Albert is running...")

    return demo_account_options, html.Div([
        html.H3("Albert Status"),
        html.Pre(read_status(),className='pre'),
        # html.Pre(str(crawler_results),className='pre') if crawler_results else None,
        # html.Pre(f"{datetime.datetime.now().strftime('%H:%M:%S')}: Albert has completed the run.",className='pre') if not session.get('web_crawler_running') else None,
        html.Br(),
    ])

def run_web_crawler(selected_accounts, selected_page_trees, selected_modules, sharepoint_upload):
    # Initialize the outputs
    crawler_results.clear()

    global stop_crawler
    stop_crawler = False
      # Write 'running' status to the file
    for account in selected_accounts:
        account_details = account.split('|')  

        for page_tree in selected_page_trees:
            # Check if the stop button has been clicked
            if stop_crawler:
                write_status(f"Albert has been stopped. at {datetime.datetime.now().strftime('%H:%M:%S')}")
                print('stopped in page tree selection')
                break

            status = f"Running domain {page_tree} for account {account_details[0]}"
            crawler_results.append(status)
            
            if page_tree == 'Competitor' and account not in ['demo_competitor@pproap.com','demo_mapcompetitor_solp@yopmail.com']:
                status = f"Competitor can only run for these accounts: ['demo_competitor@pproap.com','demo_mapcompetitor_solp@yopmail.com']"
                crawler_results.append(status)
                
                continue
            elif page_tree != 'Competitor' and account in ['demo_competitor@pproap.com','demo_mapcompetitor_solp@yopmail.com']:
                status = f"{page_tree} cannot run for this account: {account_details[0]}"
                crawler_results.append(status)
                continue
        
            if page_tree == 'Competitor':
                Firstrun = Competitor(*account_details[:])
            elif page_tree == 'PRP':
                Firstrun = PRP(*account_details[:])  
            elif page_tree == 'MarketingPro':
                Firstrun = MarketingPro(*account_details[:])
            
            Firstrun.setUp()
            Firstrun.scrapecall_writetrees()
            Firstrun.tearDown()
            status = f"Domain {page_tree} run completed for account {account_details[0]}"
            crawler_results.append(status)

        for module in selected_modules:

            # Check if the stop button has been clicked
            if stop_crawler:
                write_status(f"Albert has been stopped. at {datetime.datetime.now().strftime('%H:%M:%S')}")
                print('stopped in module selection')
                break

            # Initialize the result message for the account and module
            
            status = f"Running module {module} for account {account_details[0]}"
            crawler_results.append(status)

            if module == 'Broken_Links':
                Firstrun = Broken_Links(*account_details[:])
                Firstrun.setUp()
                Firstrun.test_load_home_page()
                Firstrun.test_multiple_broken()
                Firstrun.tearDown()

            elif module == 'Translation_and_Empty_Page':
                Firstrun=Translation_and_Empty_Page(*account_details[:])
                Firstrun.setUp()
                Firstrun.test_load_home_page()
                Firstrun.parent()
                Firstrun.tearDown()

            elif module == 'New_Tab':
                Firstrun=New_Tab(*account_details[:])
                Firstrun.setUp()
                Firstrun.test_new_tab()
                Firstrun.tearDown()

            elif module == 'T_variable':
                Firstrun=T_variable(*account_details[:])
                Firstrun.test_tvar_check()
                Firstrun.tearDown()
            status = f"Module {module} run completed for account {account_details[0]}"
            crawler_results.append(status) 

        # Check if the stop button has been clicked
        if stop_crawler:
            write_status(f"Albert has been stopped. at {datetime.datetime.now().strftime('%H:%M:%S')}")
            print('stopped after module selection')
            break

    if sharepoint_upload == 'Yes':
        aggregate(to_be_merged_folderpath)
        # upload(to_be_uploaded_filepath)
       
    write_status(f"{datetime.date.today()} {datetime.datetime.now().strftime('%H:%M:%S')}: Albert has completed the run.")  # Write 'completed' status to the file
    return crawler_results


@dash_app.callback(
    Output('adhoc-output', 'children'),
    [Input('adhoc-dropdown', 'value'),
     Input('run-crawler-button', 'n_clicks'),
     Input('scheduled-time-input', 'value'),
     Input('date-picker-single', 'date')]
)
def run_adhoc_task(selected_adhoc, n_clicks, selected_time, selected_date):
    # Initialize the outputs
    adhoc_results = []

    # Check if button is clicked, an Adhoc task is selected, and a time and date are selected
    if n_clicks and selected_adhoc and selected_time and selected_date:
        # Schedule the job for the selected date and time
        selected_date_and_time = datetime.datetime.strptime(selected_date + " " + selected_time, "%Y-%m-%d %H:%M")
        scheduler.add_job(run_adhoc_function, 'date', run_date=selected_date_and_time, args=[selected_adhoc], id='adhoc_job')
        write_status(f"{selected_date} {selected_time}: Adhoc task is scheduled.")

    return  html.Div([html.Pre(read_status(),className='pre')])

def run_adhoc_function(selected_adhoc):
    # Initialize the outputs
    adhoc_results = []

    global stop_crawler
    stop_crawler = False

    # Hardcode your account details
    account_details = ['bot.dec-d001a@hpe.com', 'Login2PRP!', 'NA', 'USA', 'English', 'T2']
    if stop_crawler:
        write_status(f"Adhoc run has been stopped at {datetime.datetime.now().strftime('%H:%M:%S')}")
        print('stopped before running Adhoc')
    

    if selected_adhoc == 'Adhoc Word Search':
        First=Adhoc_page_tree(*account_details)
        First.setUp()
        # Firstrun.test_internal_page()
        First.scrapecall_writetrees()
        First.tearDown()

        print('Now running adhoc internal login')

        # Firstrun = Adhoc_internal_login(*account_details)
        # Firstrun.setUp()
        # Firstrun.test_internal_page()
        # Firstrun.tearDown()
        if stop_crawler:
            write_status(f"Adhoc run has been stopped at {datetime.datetime.now().strftime('%H:%M:%S')}")
            print('stopped after adhoc internal login module run')
            return
        status = f"Adhoc task {selected_adhoc} run completed for account {account_details[0]}"
        adhoc_results.append(status)
    write_status(f"{datetime.date.today()} {datetime.datetime.now().strftime('%H:%M:%S')}: Adhoc task has completed the run.")  # Write 'completed' status to the file
    return adhoc_results




@dash_app.callback(
    Output('stop-output', 'children'),
    [Input('stop-crawler-button', 'n_clicks')]
)

def stop_web_crawler(_):
    global stop_crawler
    
    # Check if the stop button was clicked
    if callback_context.triggered_id is not None and 'stop-crawler-button' in callback_context.triggered_id:
        # Set stop_crawler to True to stop the crawler
        stop_crawler = True
        write_status('Albert/Adhoc has been stopped')
        # Return updated status message for regular stop
        return read_status()

if __name__ == '__main__':
    dash_app.run()

import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash import dash_table


# Read the Excel file
df = pd.ExcelFile('Fixers_list.xlsx')

# Create a dictionary of DataFrames for each sheet, excluding the last one
sheets_dict = {sheet_name: df.parse(sheet_name) for sheet_name in df.sheet_names}


layout = html.Div([
    html.Br(),
    html.Br(),
    html.Div([
        dcc.Tabs(id='tabs', value='tab-1', children=[
            dcc.Tab(label=sheet_name, value=sheet_name,className='table-content') for sheet_name in sheets_dict.keys()
        ],className='tabs2'),
        html.Div(id='tabs-content',style={'margin-left': '50px'}),
    ], style={'display': 'flex'}),
    dcc.ConfirmDialogProvider(
        children=html.Button(
            'Save Changes',
            id='save-button-1'
        ),
        id='save-button',
        message='Are you sure you want to save the changes?',
    )
],className='popup2')

@callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))

def render_content(tab):
    if tab in sheets_dict:
        # Get the columns of the DataFrame
        columns = sheets_dict[tab].columns.tolist()

        # Create a list of dictionaries for the 'columns' parameter of DataTable
        # Set 'editable' to True only for the last column
        table_columns = [{'name': i, 'id': i, 'editable': (i == columns[-1])} for i in columns]

        return html.Div([
            html.Br(),
            html.Br(),
            dash_table.DataTable(
                id='datatable',
                columns=table_columns,
                data=sheets_dict[tab].to_dict('records'),
                style_data={'backgroundColor': '#d3dce6','color':'rgb(0,0,0)'},
                style_header={'backgroundColor': '#000000', 'fontWeight': 'bold', 'text-align': 'center'},
                style_cell={'color': 'white', 'text-align': 'center','width': '1%', 'minWidth': '100px', 'maxWidth': '500px'},
                style_table={'width': '100%', 'max-width': '100%','margin-left': 'auto', 'margin-right': 'auto'},

                active_cell={'row': 0, 'column': 0},
                
            )
        ])
    else:
        return html.Div([
            html.H3(f"Select the Fixerlist Tab")
        ])


@callback(Output('save-button', 'n_clicks'),
              [Input('save-button', 'submit_n_clicks')],
              [State('datatable', 'data'),
               State('tabs', 'value')])
def save_changes(n_clicks, rows, tab):
    if n_clicks > 0:
        # Convert the updated rows back to a DataFrame
        df = pd.DataFrame(rows)

        # Update the corresponding DataFrame in the dictionary
        sheets_dict[tab] = df

        # Write the updated DataFrames back to the Excel file
        with pd.ExcelWriter('fixers__.xlsx') as writer:
            for sheet_name, df in sheets_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        return 0  # Reset the number of button clicks to 0

    return n_clicks  # If the button hasn't been clicked, return the current number of clicks




from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import pandas as pd
from dash import dash_table

# Read the Excel file
df = pd.read_excel('Ad hoc Requests\Aruba Series names - Adhoc request.xlsx')
layout_2 = html.Div([
    html.Br(),
    html.Br(),
    
    html.Div([
        dash_table.DataTable(
            id='datatable-2',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            style_data={'backgroundColor': '#d3dce6','color':'rgb(0,0,0)'},
                style_header={'backgroundColor': '#000000', 'fontWeight': 'bold', 'text-align': 'center'},
                style_cell={'color': 'white', 'text-align': 'center','width': '1%', 'minWidth': '100px', 'maxWidth': '500px'},
                style_table={'width': '100%', 'max-width': '100%','margin-left': 'auto', 'margin-right': 'auto'},
            editable=True,
            # active_cell={'row': 0, 'column': 0},
        ),

        html.Div([
            html.Button('Add Row', id='add-row-button'),  # Button for adding rows

            dcc.ConfirmDialogProvider(
                children=html.Button(
                    'Save',
                    id='save-button-3'
                ),
                id='save-button-2',
                message='Are you sure you want to save the changes?',
            )
        ], className='buttons')
    ], className='container')
], className='popup2')

# Callback for adding rows
@callback(Output('datatable-2', 'data'),
          [Input('add-row-button', 'n_clicks')],
          [State('datatable-2', 'data'),
           State('datatable-2', 'columns')])
def add_row(n_clicks, rows, columns):
    if n_clicks:
        rows.append({c['id']: '' for c in columns})
    return rows

@callback(Output('save-button-2', 'n_clicks'),
          [Input('save-button-2', 'submit_n_clicks')],
          [State('datatable-2', 'data')])
def save_changes(n_clicks, table_data):
    if n_clicks is not None:
        # Convert the updated rows back to a DataFrame
        df = pd.DataFrame(table_data)
        df.to_excel('Ad hoc Requests\Aruba Series names - Adhoc request.xlsx', index=False)
        return 0  # Reset the number of button clicks to 0
    return n_clicks  # If the button hasn't been clicked, return the current number of clicks
    

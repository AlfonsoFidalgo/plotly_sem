import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

import psycopg2 as pc
import db_credentials as db

app = dash.Dash()

# conn = pc.connect(database=db.credentials['db_name'],
#                                user=db.credentials['db_user'],
#                                password=db.credentials['db_pw'],
#                                host=db.credentials['db_host'],
#                                port=db.credentials['db_port'])
#
# cur = conn.cursor()
# cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day > current_date - 30")
# conn.commit()
# data = cur.fetchall()
# df = pd.DataFrame(data)
#
# df.columns = ['day', 'source', 'account_id', 'account_name',
#               'campaign_id', 'campaign_name', 'adgroup_id',
#                'adgroup_name', 'impressions', 'clicks',
#                 'cost', 'leads', 'listing_price']
#
# df.to_csv('dashboard_161118.csv')
df = pd.read_csv('dashboard_161118.csv')

app.layout = html.Div([
    #ACCOUNT AND SOURCE SELECTOR
    html.Div([
        html.Label('Select source:'),
        dcc.Dropdown(
            id='source_selector',
            options=[{'label': i, 'value': i} for i in df['source'].unique()],
            value=['google_ads', 'bing_ads'],
            multi=True
        ),
    ],
        style={'width': '48%','height': '15%', 'display': 'inline-block'}),

    html.Div([
        html.Label('Select account:'),
        dcc.Dropdown(
            id='account_selector',
            options=[{'label': i, 'value': i} for i in df['account_name'].unique()],
            value=[acc for acc in df['account_name'].unique().tolist()],
            multi=True
        ),
    ],
        style={'width': '48%','height': '15%', 'float': 'right', 'display': 'inline-block'}),


    html.Div([
        html.H3('Select some metrics')
    ]),
    #KPI SELECTOR
    html.Div([
        html.Label('Select first KPI:'),
        dcc.Dropdown(
            id='kpi_left',
            options=[{'label': 'Leads', 'value': 'leads'},
                     {'label': 'Cost', 'value': 'cost'},
                     {'label': 'Clicks', 'value': 'clicks'},
                     {'label': 'CPA', 'value': 'cpa'},
                     {'label': 'CPC', 'value': 'cpc'},
                     {'label': 'CTR', 'value': 'ctr'}],
            value='cpa',
            multi=False
        )
    ]),

    html.Div([
        html.Label('Select second KPI:'),
        dcc.Dropdown(
            id='kpi_right',
            options=[{'label': 'Leads', 'value': 'leads'},
                     {'label': 'Cost', 'value': 'cost'},
                     {'label': 'Clicks', 'value': 'clicks'},
                     {'label': 'CPA', 'value': 'cpa'},
                     {'label': 'CPC', 'value': 'cpc'},
                     {'label': 'CTR', 'value': 'ctr'}],
            value='leads',
            multi=False
        )
    ]),

    dcc.Graph(id='daily_performance_plot')
], style={'padding': 10})

@app.callback(Output('daily_performance_plot', 'figure'),
    [Input('source_selector', 'value'),
     Input('account_selector', 'value'),
     Input('kpi_left', 'value'),
     Input('kpi_right', 'value')])
def update_graph(source, account, kpi_l, kpi_r):
    daily = df[(df['source'].isin(source)) & (df['account_name'].isin(account))].groupby(['day']).sum().reset_index()
    daily['cpa'] = daily['cost'] / daily['leads']
    daily['ctr'] = daily['clicks'] / daily['impressions']
    daily['cpc'] = daily['cost'] / daily['clicks']


    leads = go.Scatter(
        x=daily['day'].unique(),
        y=daily[kpi_l],
        name=kpi_l,
        mode='lines',
        yaxis='y2',
        opacity=1,
        # fill='tozeroy',
        line={'width': 2, 'smoothing': 1}
    )


    cpa = go.Scatter(
        x=daily['day'].unique(),
        y=daily[kpi_r],
        name=kpi_r,
        mode='lines',
        opacity=1,
        # fill='tozeroy',
        line={'width': 2, 'smoothing': 1}
    )


    return {
        'data': [cpa, leads],
        'layout': go.Layout(
            xaxis={'title': 'Day'},
            yaxis={'title': kpi_l},
            yaxis2={'overlaying': 'y', 'side': 'right', 'title': kpi_r},
            # width=500,
            height=650,
        )
    }


if __name__ == '__main__':
    app.run_server()

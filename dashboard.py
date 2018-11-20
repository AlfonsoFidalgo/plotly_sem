import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_auth
import datetime

import psycopg2 as pc
import db_credentials as db

USERNAME_PASSWORD_PAIRS = [
    ['afidalgo', 'r93fuzCz:+FR[PG{']
]

app = dash.Dash()
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)



conn = pc.connect(database=db.credentials['db_name'],
                               user=db.credentials['db_user'],
                               password=db.credentials['db_pw'],
                               host=db.credentials['db_host'],
                               port=db.credentials['db_port'])

cur = conn.cursor()
cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day > current_date - 80")
conn.commit()
data = cur.fetchall()
df = pd.DataFrame(data)

df.columns = ['day', 'source', 'account_id', 'account_name',
              'campaign_id', 'campaign_name', 'adgroup_id',
               'adgroup_name', 'impressions', 'clicks',
                'cost', 'leads', 'listing_price']

df.to_csv('raw_data.csv')
# df = pd.read_csv('dashboard_161118.csv')
df['week_num'] = df['day'].apply(lambda x: x.isocalendar()[1])
df['month'] = df['day'].apply(lambda x: x.month)


app.layout = html.Div([
    #ACCOUNT AND SOURCE SELECTOR
    html.Div([
        html.H2('Filters'),
        html.Div([
            html.Label('Source filter:'),
            dcc.Dropdown(
                id='source_selector',
                options=[{'label': i, 'value': i} for i in df['source'].unique()],
                value=['google_ads', 'bing_ads'],
                multi=True
            ),
            ]),

        html.Div([
            html.Label('Account filter:'),
            dcc.Dropdown(
                id='account_selector',
                options=[{'label': i, 'value': i} for i in df['account_name'].unique()],
                value=[acc for acc in df['account_name'].unique().tolist()],
                multi=True
            ),
        ])
    ]
    ),


    html.Div([
        html.H2('Metrics'),
            #KPI SELECTOR
        html.Div([
            html.Label('Right axis metric:'),
            dcc.Dropdown(
                id='kpi_left',
                options=[{'label': 'Leads', 'value': 'leads'},
                         {'label': 'Cost', 'value': 'cost'},
                         {'label': 'Clicks', 'value': 'clicks'},
                         {'label': 'CPA', 'value': 'cpa'},
                         {'label': 'CPC', 'value': 'cpc'},
                         {'label': 'CTR', 'value': 'ctr'},
                         {'label': 'Avg. lead price', 'value': 'avg_price'}],
                value='cpa',
                multi=False
            )
        ]),

        html.Div([
            html.Label('Left axis metric:'),
            dcc.Dropdown(
                id='kpi_right',
                options=[{'label': 'Leads', 'value': 'leads'},
                         {'label': 'Cost', 'value': 'cost'},
                         {'label': 'Clicks', 'value': 'clicks'},
                         {'label': 'CPA', 'value': 'cpa'},
                         {'label': 'CPC', 'value': 'cpc'},
                         {'label': 'CTR', 'value': 'ctr'},
                         {'label': 'CVR', 'value': 'cvr'},
                         {'label': 'Avg. lead price', 'value': 'avg_price'}],
                value='leads',
                multi=False
            )
        ])
    ]
    ),

    html.Div([
    html.Label('Time resolution:'),
        dcc.Dropdown(
            id='time_res',
            options=[{'label': 'Daily', 'value': 'day'},
                     {'label': 'Weekly', 'value': 'week_num'},
                     {'label': 'Monthly', 'value': 'month'}],
            value='day',
            multi=False
        )
    ]),

    dcc.Graph(id='daily_performance_plot')
], style={'padding': 10})

@app.callback(Output('daily_performance_plot', 'figure'),
    [Input('source_selector', 'value'),
     Input('account_selector', 'value'),
     Input('kpi_left', 'value'),
     Input('kpi_right', 'value'),
     Input('time_res', 'value')])
def update_graph(source, account, kpi_l, kpi_r, time_r):

    df_plot = df[(df['source'].isin(source)) & (df['account_name'].isin(account))].groupby([time_r]).sum().reset_index()
    df_plot['cpa'] = df_plot['cost'] / df_plot['leads']
    df_plot['ctr'] = df_plot['clicks'] / df_plot['impressions']
    df_plot['cpc'] = df_plot['cost'] / df_plot['clicks']
    df_plot['cvr'] = df_plot['leads'] / df_plot['clicks']
    df_plot['avg_price'] = df_plot['listing_price'] / df_plot['leads']


    y1 = go.Scatter(
        x=df_plot[time_r].unique(),
        y=df_plot[kpi_l],
        name=kpi_l,
        mode='lines',
        yaxis='y2',
        opacity=1,
        # fill='tozeroy',
        line={'width': 2, 'smoothing': 1}
    )


    y2 = go.Scatter(
        x=df_plot[time_r].unique(),
        y=df_plot[kpi_r],
        name=kpi_r,
        mode='lines',
        opacity=1,
        # fill='tozeroy',
        line={'width': 2, 'smoothing': 1}
    )


    return {
        'data': [y2, y1],
        'layout': go.Layout(
            xaxis={'title': time_r},
            yaxis={'title': kpi_r},
            yaxis2={'overlaying': 'y', 'side': 'right', 'title': kpi_l},
            # width=500,
            height=650,
        )
    }


if __name__ == '__main__':
    app.run_server()

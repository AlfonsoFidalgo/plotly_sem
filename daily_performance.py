import pandas as pd
import numpy as np
import psycopg2 as pc
import db_credentials as db
import datetime
import plotly.offline as pyo
import plotly.graph_objs as go


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

daily = df[['day', 'cost', 'leads']].groupby(['day']).sum().reset_index()
daily['cpa'] = daily['cost'] / daily['leads']

#MOVING AVERAGES FROM LEADS AND CPA
daily['cost_7'] = daily.rolling(window=7)['cost'].sum()
daily['leads_7'] = daily.rolling(window=7)['leads'].sum()
daily['cpa_7'] = daily['cost_7'] / daily['leads_7']
daily['leads_7_avg'] = daily['leads_7'] / 7

#TRACES
cpa = go.Scatter(
    x=daily['day'],
    y=daily['cpa'],
    name='cpa',
    mode='lines',
    opacity=0.4,
    line={'width': 2, 'smoothing': 1, 'shape': 'spline'}
)

cpa_7 = go.Scatter(
    x=daily['day'],
    y=daily['cpa_7'],
    name='7 days avg. CPA',
    line={'width': 3}
)

leads_7 = go.Scatter(
    x=daily['day'],
    y=daily['leads_7_avg'],
    name='7 days avg. Leads',
    yaxis='y2',
    line={'width': 3}
)

leads = go.Scatter(
    x=daily['day'],
    y=daily['leads'],
    name='leads',
    mode='lines',
    yaxis='y2',
    opacity=0.4,
    line={'width': 2, 'smoothing': 1, 'shape': 'spline'}

)

data = [cpa, cpa_7, leads, leads_7]
layout = go.Layout(
    title='Daily CPA & Lead volume',
    yaxis=dict(title='CPA'),
    yaxis2=dict(
        overlaying='y',
        side='right',
        title='Leads'
    ))

figure = go.Figure(data=data, layout=layout)

pyo.plot(figure, filename='daily_performance.html')

import pandas as pd
import numpy as np
# from io import StringIO
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
# cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day > current_date - 50")
cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day BETWEEN '2018-10-01' AND '2018-11-11'")
conn.commit()
data = cur.fetchall()
df = pd.DataFrame(data)

df.columns = ['day', 'source', 'account_id', 'account_name', 'campaign_id', 'campaign_name', 'adgroup_id', 'adgroup_name', 'impressions', 'clicks', 'cost', 'leads', 'listing_price']
df['week_number'] = df['day'].apply(lambda x: x.isocalendar()[1])

weekly = df[['week_number', 'source', 'cost', 'leads']].groupby(['week_number', 'source']).sum().reset_index()
weekly['cpa'] = weekly['cost'] / weekly['leads']

##GRAPHS
google = go.Bar(
    x=weekly['week_number'].unique().tolist(),
    y=weekly[weekly['source'] == 'google_ads']['cpa'],
    name='Google Ads'
    )

bing = go.Bar(
    x=weekly['week_number'].unique().tolist(),
    y=weekly[weekly['source'] == 'bing_ads']['cpa'],
    name='Bing Ads'
)

data = [google, bing]
layout = go.Layout(
    title='Weekly cpa by source')

fig = go.Figure(data=data, layout=layout)
pyo.plot(fig, filename='weekly_cpa_source.html')

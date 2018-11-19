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
cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day > current_date - 15")
# cur.execute("SELECT * FROM heycar_report.marketing_sea_performance_daily WHERE day BETWEEN '2018-10-29' AND '2018-11-11'")
conn.commit()
data = cur.fetchall()
df = pd.DataFrame(data)

df.columns = ['day', 'source', 'account_id', 'account_name', 'campaign_id', 'campaign_name', 'adgroup_id', 'adgroup_name', 'impressions', 'clicks', 'cost', 'leads', 'listing_price']
df['week_number'] = df['day'].apply(lambda x: x.isocalendar()[1])

weekly = df[['week_number', 'source', 'account_name', 'cost', 'leads', 'listing_price']].groupby(['week_number', 'source', 'account_name']).sum().reset_index()
weekly['cpa'] = weekly['cost'] / weekly['leads']
weekly['avg_price'] = weekly['listing_price'] / weekly['leads']

last_week = weekly[weekly['week_number'] == weekly['week_number'].max()].sort_values('cost', ascending=False)
week_before = weekly[weekly['week_number'] == weekly['week_number'].min()].sort_values('cost', ascending=False)
weekly_summary_raw = pd.merge(last_week, week_before, how='left', on=['source', 'account_name'])
weekly_summary_raw['cost_var'] = (weekly_summary_raw['cost_x'] - weekly_summary_raw['cost_y']) / weekly_summary_raw['cost_y']
weekly_summary_raw['leads_var'] = (weekly_summary_raw['leads_x'] - weekly_summary_raw['leads_y']) / weekly_summary_raw['leads_y']
weekly_summary_raw['price_var'] = (weekly_summary_raw['avg_price_x'] - weekly_summary_raw['avg_price_y']) / weekly_summary_raw['avg_price_y']
weekly_summary_raw['cpa_var'] = (weekly_summary_raw['cpa_x'] - weekly_summary_raw['cpa_y']) / weekly_summary_raw['cpa_y']

wow_summary = weekly_summary_raw[['source', 'account_name', 'cost_x', 'cost_var', 'leads_x', 'leads_var', 'cpa_x', 'cpa_var', 'avg_price_x', 'price_var']]


###TABLE GRAPH
trace = go.Table(
    header=dict(values=['Source', 'Account', 'Cost', 'Cost Var%', 'Leads', 'Leads Var%', 'CPA', 'CPA Var%', 'Avg. Listing Price', 'Price Var%'],
                line = dict(color='#002937'),
                fill=dict(color='#002937'),
                font=dict(color='#ffffff'),
                align = ['left'] * 5),

    cells=dict(values=[wow_summary['source'],
                       wow_summary['account_name'],
                       round(wow_summary['cost_x'], 2),
                       round(wow_summary['cost_var'] * 100, 2),
                       wow_summary['leads_x'],
                       round(wow_summary['leads_var'] * 100, 2),
                       round(wow_summary['cpa_x'], 2),
                       round(wow_summary['cpa_var'] * 100, 2),
                       round(wow_summary['avg_price_x'], 2),
                       round(wow_summary['price_var'] * 100, 2)
                       ],
                       line = dict(color='#D2D2D2'),
                       fill = dict(color='#EEEEEE'),
                       # font=dict(color='#ffffff'),
                       align = ['left'] * 5))

data = [trace]
pyo.plot(data, filename = 'wow_summary.html')

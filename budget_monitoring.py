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
cur.execute("""SELECT
                day, sum(cost)
                FROM heycar_report.marketing_sea_performance_daily
                WHERE day BETWEEN '2018-11-01' AND '2018-11-30'
                GROUP BY 1 ORDER BY 1 ASC;""")
conn.commit()
data = cur.fetchall()
df = pd.DataFrame(data)
df.columns = ['date', 'cost']
df['cum_sum'] = df['cost'].cumsum()
#df['day'] = df['date'].apply(lambda x: int(x.split('-')[2]))
df['day'] = df['date'].apply(lambda x: x.day)
# df.to_csv('daily_spend.csv')

##Dataframe for daily targets
days_in_month = 30
monthly_budget = 800000
daily_target = monthly_budget / days_in_month
daily_targets = np.arange(daily_target, monthly_budget + 1, daily_target)
daily_targets_df = pd.DataFrame(data=daily_targets, columns=['daily_target'])
days = np.arange(1, days_in_month + 1)
days_df = pd.DataFrame(data=days, columns=['days'])
days_df['spend_target'] = daily_targets_df



daily_target = go.Scatter(
    x=days_df['days'],
    y=days_df['spend_target'],
    mode='lines',
    name='Spend target'
)

daily_spend = go.Scatter(
    x = df['day'],
    y = df['cum_sum'],
    mode = 'lines',
    name = 'Cumulative Spend'
)

data = [daily_spend, daily_target]

layout = go.Layout(
    title = 'Cumulative spend vs. monthly budget'
)
fig = go.Figure(data=data,layout=layout)
pyo.plot(fig, filename='budget_monitoring.html')

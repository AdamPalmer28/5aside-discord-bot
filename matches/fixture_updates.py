"""
Handles the updating of fixtures from the website
"""
import pandas as pd
from datetime import datetime as dt

def fixture_data_format(data):
    "Basic data formatting for fixtures"

    data['Date'] = pd.to_datetime(data['Date'])
    data['Time'] = pd.to_datetime(data['Time'], format='%H:%M').dt.time

    # combine date and time
    data['Datetime'] = data.apply(lambda x: dt.combine(x['Date'], x['Time']), axis=1)

    # determine winner
    data['Winner'] = data.apply(lambda x: \
                x['Home'] if x['Home score'] > x['Away score'] else \
                ('Draw' if x['Home score'] == x['Away score'] else x['Away']), axis=1)
    
    return data

"""
Scrapes the league website for the fixtures and results of the league.
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup

url = "https://www.leisureleagues.net/league/fixture-list/aqua-vale-swimming-fitness-centre/aylesbury-thursday/premier-league"

def get_league_matches():
    """
    Request HTML page for scraping of fixture data
    Get the league matches from the league website - providing the results of the league
    where possible.
    """
    # out dataframe
    data = pd.DataFrame(columns = ['Date','Time', 'Home','Away', 'Home score','Away score'])
    
    # HTML request
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    fixtures = soup.find(attrs={'class':"table table-bordered"})

    thead_count, tbody_count = 0, 0

    for ind, elmement in enumerate(fixtures.children):
        if elmement.name == 'thead':
            
            if thead_count % 2 == 0:
                # date
                date = elmement.get('class')
            thead_count += 1

        elif elmement.name == 'tbody':

            for tr in elmement.find_all('tr', attrs={'data-date': date}):
                
                # fixture
                time, _, t1, s1, _, s2, t2= tr.find_all('td')
                # create row
                row = {'Date': date[0], 'Time': time.text, 
                    'Home': (t1.text).strip(), 
                    'Away': (t2.text).strip(), 
                    'Home score': (s1.text), 
                    'Away score': (s2.text)}
                
                # append row to data
                data = pd.concat([data, pd.DataFrame([row])], ignore_index=True)

    # track pending results
    pending = data[(data['Home score'] == '\n-\n') | (data['Away score'] == '\n-\n')]
    data['Pending'] = False
    data.loc[pending.index, 'Pending'] = True

    # data cleaning
    for col in ['Home score', 'Away score']:
        data[col] = data[col].str.replace("\n", "")
        data[col] = data[col].str.replace("-", "0")

    data['Home score'] = data['Home score'].astype(int)
    data['Away score'] = data['Away score'].astype(int)

    # time formatting
    data['Time'] = pd.to_datetime(data['Time'], format='%H:%M').dt.time 

    return data
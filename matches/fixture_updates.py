"""
Handles the updating of fixtures from the website
"""
import pandas as pd
from datetime import datetime as dt

admin_id = 184737297734959104

def fixture_data_format(data):
    "Basic data formatting for fixtures"

    data['Date'] = pd.to_datetime(data['Date'])
    data['Time'] = pd.to_datetime(data['Time'], format='%H:%M:%S').dt.time

    # combine date and time
    data['Datetime'] = data.apply(lambda x: dt.combine(x['Date'], x['Time']), axis=1)

    # determine winner
    data['Winner'] = data.apply(lambda x: \
                x['Home'] if x['Home score'] > x['Away score'] else \
                ('Draw' if x['Home score'] == x['Away score'] else x['Away']), axis=1)
    
    return data


async def check_new_fixture_data(new_data: pd.DataFrame, old_data: pd.DataFrame, 
                                 path: str, bot, channel_id):
    """
    Function to update the fixture data with new data from the latest website scrape.
    There are 3 cases which can occur:

    - case 1: new season started
    - case 2: new results added
        - case 2.1: new team
    - case 3: no update 
    """
    # fix time column (remove seconds)
    new_data = fixture_data_format(new_data)

    # case 1: new season
    if all(new_data['Date'] != old_data['Date']):    
        latest_date = dt.strptime(old_data['Date'].iloc[-1], '%Y-%m-%d')

        #old_season_path = f'//TRUENAS/Misc_storage/5aside_discord_bot/league_data/old_seasons/'
        old_season_path = path + f'/league_data/old_seasons/'
        old_data.to_csv(old_season_path+f'Season-{latest_date.strftime("%Y-%m-%d")}.csv', index=False)
        
        return new_data, 1
    
    # case 2: check for new results
    elif any(new_data['Pending'] != old_data['Pending']):
        # new results added
        new_results = new_data[new_data['Pending'] != old_data['Pending']]

        # display new results
        latest_results_msg = f'**New results extracted**:\n'
        latest_results_msg += 'The latest fixtures:\n'

        await channel.send(latest_results_msg)

        results = new_results[['Time','Home','Home score','Away score','Away']]
        await channel.send(f'```{results.to_string(index=False)}```')
        


        # case 2.1: new team
        old_data_teams = old_data[new_data['Pending'] != old_data['Pending']]
        n_team = set(new_results['Home']).union(set(new_results['Away']))
        o_team = set(old_data_teams['Home']).union(set(old_data_teams['Away']))

        async def new_team(new, old):
            "Helper function - msgs about team change"
            msg = f"\n\n**New team added**: {new} (previously was {old})"
            await channel.send(msg)

        # check for new team in latest fixtures
        for (n_hteam, n_ateam, o_hteam, o_ateam) in zip(new_results['Home'], new_results['Away'], \
                                      old_data_teams['Home'], old_data_teams['Away']):
            
            if (n_hteam != o_hteam) & (o_hteam not in n_team):
                await new_team(n_hteam, o_hteam)

            if (n_ateam != o_ateam) & (o_ateam not in n_team):
                await new_team(n_ateam, o_ateam)
        
        return new_data, 2

    # case 3: no update
    else:
        # msg Admin - tried to pull new results but none found
        admin = bot.get_user(admin_id)
        await admin.send(f'Fixture update: No new results found')

        return old_data, 3

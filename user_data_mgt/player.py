from pandas import DataFrame

class Player:
    """
    Data structure for a player (discord user)
    """
    def __init__(self, 
                name: list[str], 
                id: str,
                goal: dict = {}, 
                assist: dict = {},
                availability: dict = {},
                paid: dict = {},
                motm: dict = {},
                vote: list = {},
                 ):

        # player info
        self.name = name
        self.display_name = name[0].title()
        self.id = id

        # stats
        self.goal = goal
        self.assist = assist

        # availability
        self.availability = availability
        self.paid = paid

        # motm
        self.motm = motm
        self.vote = vote

        # emoji
        self.emoji = None

# =============================================================================

def player_stats(team, results, team_name = 'Earth Wind and Maguire'):
    """
    Creates a dataframe of player stats

    columns = player | won | lost | draw | goals | assists | motm 
                    avg gf | avg ga | avg gd | avg pts

    results: dataframe of our results
    """
    def get_pwld(aval):
        "Get the number of games [won, lost, draw, gf, ga] from fixture data"
        w, l, d, g, a = 0, 0, 0, 0, 0

        for date, val in aval.items():
            if val != 'yes':
                continue
            
            try:
                match = results.loc[results['Date'] == date].iloc[0]
            except:
                continue
            
            if match['Pending'] == True:
                continue

            if match['Winner'] == team_name:
                w += 1
            elif match['Winner'] == 'Draw':
                d += 1
            else:
                l += 1

            g += match['Home score'] if match['Home'] == team_name else match['Away score']
            a += match['Away score'] if match['Home'] == team_name else match['Home score']
        return w, l, d, g, a
      

    name, played, won, lost, draw, goals, assists = [], [], [], [], [], [], []
    motm, avg_gf, avg_ga, avg_gd, avg_pts = [], [], [], [], []

    for id, user in team.items():
        name.append(user.display_name)

        w, l, d, g, a, = get_pwld(user.availability)

        p = w + l + d
        played.append( p ), avg_pts.append( ((w*2 + d)/p if p!=0 else 0) )
        won.append( w ), lost.append( l ), draw.append( d )
        
        avg_gf.append( (g/p if p!=0 else 0) ), 
        avg_ga.append( (a/p if p!=0 else 0) )
        avg_gd.append( ((g-a)/p if p!=0 else 0) )
        

        goals.append( sum(user.goal.values()) )
        assists.append( sum(user.assist.values()) )
        motm.append( len(user.motm) )

    # make final stats table
    df = DataFrame({'Name': name,
                    'played': played,
                    'won': won,
                    'draw': draw,
                    'lost': lost,
                    #'avg_gf': avg_gf,
                    #'avg_ga': avg_ga,
                    'avg_gd': avg_gd,
                    #'avg_pts': avg_pts,
                    'assists': assists,
                    'goals': goals,
                    'motm': motm,
                    })
    
    # round columns: avg_gf, avg_ga, avg_gd, avg_pts
    #df = df.round({'avg_gf': 1, 'avg_ga': 1, 'avg_gd': 1, 'avg_pts': 1})
    df = df.round({'avg_gd': 1})

    return df



        
        





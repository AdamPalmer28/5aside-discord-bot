"""
Data structure for a player (discord user)
"""

class Player:
    def __init__(self, 
                name: list[str], 
                id: str,
                goal: dict = {}, 
                assist: dict = {},
                availability: dict = {},
                paid: dict = {},
                motm: dict = {},
                motm_vote: list = [],
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
        self.motm_vote = motm_vote

from pandas import DataFrame

def player_stats(team, results):
    """
    Creates a dataframe of player stats

    columns = player | won | lost | draw | goals | assists | motm 
                    avg gf | avg ga | avg gd | avg pts
    """
    def get_pwld(aval):
        "Get the number of games [won, lost, draw, gf, ga] from fixture data"
        pass

    name, played, won, lost, draw, goals, assists = [], [], [], [], [], [], []
    motm, avg_gf, avg_ga, avg_gd, avg_pts = [], [], [], [], []

    for ic, user in team.items():
        name.append(user.display_name)

        w, l, d, g, a, = get_pwld(user.availability)

        p = w + l + d
        played.append(p), avg_pts.append((w*2 + d)/p)
        won.append(w), lost.append(l), draw.append(d)
        avg_gf.append(g/p), avg_ga.append(a/p), avg_gd.append((g-a)/p)

        goals.append(user.goal.values().sum())
        assists.append(user.assist.values().sum())
        motm.append(len(user.motm))

    # make final stats table
    df = DataFrame({'played': played,
                    'won': won,
                    'lost': lost,
                    'draw': draw,
                    'goals': goals,
                    'assists': assists,
                    'motm': motm,
                    'avg_gf': avg_gf,
                    'avg_ga': avg_ga,
                    'avg_gd': avg_gd,
                    'avg_pts': avg_pts,
                    })
    
    # round columns: avg_gf, avg_ga, avg_gd, avg_pts
    df = df.round({'avg_gf': 1, 'avg_ga': 1, 'avg_gd': 1, 'avg_pts': 1})



        
        





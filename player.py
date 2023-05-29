class Player:
    def __init__(self, name: str, discord_id: str,
                 goals: int = 0, 
                 assists: int = 0, 
                 motm: int = 0,
                 games_played: int = 0,
                 games_won: int = 0):

        # player info
        self.name = name
        self.discord_id = discord_id

        # stats
        self.goals = goals
        self.assists = assists
        self.motm = motm

        # games played and games won
        self.games_played = games_played
        self.games_won = games_won

        self.winrate = self.games_won / self.games_played


    

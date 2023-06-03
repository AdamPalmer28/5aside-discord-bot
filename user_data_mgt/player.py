"""
Data structure for a player (discord user)
"""

class Player:
    def __init__(self, 
                name: str, 
                discord_id: str,
                goals: dict = {}, 
                assists: dict = {},
                availability: dict = {},
                motm: dict = {},
                motm_votes: dict = {},
                 ):

        # player info
        self.name = name
        self.discord_id = discord_id

        # stats
        self.goals = goals
        self.assists = assists

        # availability
        self.availability = availability

        # motm
        self.motm = motm
        self.motm_votes = motm_votes


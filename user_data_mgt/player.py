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


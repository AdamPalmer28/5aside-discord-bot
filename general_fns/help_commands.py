    

def user_help(bot):
    "Provide user with help messages on how to interact with the bot"

    @bot.command()
    async def commands(ctx):
        """displays help message for users"""

        help_msg = '__**5aside discord bot**__\n\n'
        
        content = [
        '__**Avaliability**__',
        '*!available <yes/no/maybe> <player> <game date>*   -   mark your avaliability for this week',
        '*!paid <yes/no> <player> <game date>*   -   mark if you have paid, (player is optional input)',
        '*!outstanding*   -   show player outstanding payments',
        '',
        '__**Results:**__',
        '*!next*   -   information about the next game',
        '*!recent*   -   show our recent results',
        '*!table*   -   show the league table',
        '*!stats*   -   show player stats for the season',
        '',
        '__**Player stats**__',
        '*!goal <num of goals> <player> <game date>*   -   set goals for a player', 
        '*!assist <num of assists> <player> <game date>*   -   set assists for a player',
        '*!motm <player> <game date>*   -   vote motm for a player',
        '',
    
        
        ]

        help_msg += '\n'.join(content)
        await ctx.send(help_msg)
    

def user_help(bot):
    "Provide user with help messages on how to interact with the bot"

    @bot.command()
    async def commands(ctx):
        """displays help message for users"""

        help_msg = '__**5aside discord bot**__\n\n'
        
        content = [
        '__**Results:**__',
        '!next   -   information about the next game',
        '!recent   -   show our recent results',
        '!table   -   show the league table',
        '!stats   -   show player stats for the season',
        '',
        '__**Avaliability**__',
        '!outstanding   -   show player outstanding payments',
        '!available  yes/no/maybe   -   mark your avaliability (optional inputs)',
        '!paid  yes/no   -   mark if you have paid (optional inputs)',
        '',
        '__**Player stats**__',
        '!goal  number   -   (optional inputs)', 
        '!assist  number  -   (optional inputs)',
        '!vote  player   -   vote motm player',
        '',
        "**Optional inputs** - *player and game_date are optional inputs, if not provide it presume you are the player and game_date is more relevant date*",
        '',
        ]

        help_msg += '\n'.join(content)
        await ctx.send(help_msg)
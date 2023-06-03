    

def user_help(bot):
    "Provide user with help messages on how to interact with the bot"

    @bot.command()
    async def commands(ctx):
        """displays help message for users"""

        help_msg = '__**5aside discord bot**__\n\n'
        
        content = [
        '__**Avaliability**__',
        '*!avaliable <yes/no/maybe>*   -   mark your avaliability for this week',
        '*!paid <yes/no> <player>*   -   mark if you have paid, (player is optional input)',
        '*!outstanding*   -   show player outstanding payments',
        '',
        '__**Fixtures**__',
        '*!next*   -   information about the next game',
        '*!recent*   -   show our recent results',
        '*!table*   -   show the league table',
        '',
        '__**Player stats**__',
        '*!motm vote <player>*   -   vote for MOTM of most recent week',
        # '*!goal_add <player> <number of goals> <game date>*   -   add player goals',
        # '*!goal_remove <player> <number of goals> <game date>*   -   remove player goals',
        # '*!assist_add <player> <number of assist> <game date>*   -   add player assist',
        # '*!assist_remove <player> <number of assist> <game date>*   -   remove player assist',
        '',
        '__**Team set up**__',
        '*!player_add <name> <discord_id>*   -   add player to team',
        '*!player_remove <name> <discord_id>* -remove player from team',
        
        ]

        help_msg += '\n'.join(content)
        await ctx.send(help_msg)
from discord.ext import commands
from .player import Player, player_stats
import json
from datetime import datetime as dt
import discord

class Team(commands.Cog):

    def __init__(self, bot, fixtures, path, channel):
        
        self.bot = bot
        self.bot_id = 1112735643114680361

        self.path = path
        self.load_team()

        self.channel = channel
        
        self.fixtures = fixtures

        self.admin_users = [184737297734959104]

        self.captain_id = 184737297734959104 #265576326788808704 # Jack
        self.captain = self.bot.get_user(self.captain_id)

        # team emoji
        self.emojis_hc = {
            'Adam': '🤓',
            'Tommy':'🧑‍🦽',
            'Matty': '🐐',
            'Jack': '🔞',
            'Tom': '👌',
            'Ben': '🅱️',
            'James': discord.utils.get(bot.emojis, name="CSAFMdmUAAAFzaH"),
            'Tk': '👻',
            'Noz': '🔥',
        }
        # give users their emojis
        for id, user in self.team.items():
            for name in user.name:
                emoji = self.emojis_hc.get(user.display_name, False)
                if emoji:
                    user.emoji = emoji
                    break


        # create team data
        answer_data = ['availability', 'paid', 'vote']
        self.get_team_data(answer_data, group_answers = True)
        self.get_team_data(['goal', 'assist', 'motm'])

        # start bot event functions
        self.init_bot_event()


    # =========================================================================
    # --------------------- Class functions -----------------------------------
    # =========================================================================

    def get_team_data(self, attrs: list[str], group_answers: bool = False):
        """
        Creates team data for each fixture
        
        attrs: list of user data attributes 
        group_answers: bool - if True, group player answers together
        """
        
        for attr in attrs:
            setattr(self, attr, {}) # create attribute

            for id, user in self.team.items():
                name = user.display_name
                user_dict = getattr(user, attr) # get user data

                for date, answer in user_dict.items():
                    # loop through user data (dates)
                    
                    if (attr == 'paid') & (user.availability.get(date, 'no') != 'yes'): 
                        # if user is not avaliable, skip
                        continue

                    if group_answers:
                        # group answers will record names for each response
                        
                        if date not in getattr(self, attr):
                            # if date doesn't exist, create it
                            getattr(self, attr)[date] = {}
                        if answer not in getattr(self, attr)[date]:
                            # if answer doesn't exist, create it
                            getattr(self, attr)[date][answer] = []

                        # add name to answer
                        getattr(self, attr)[date][answer].append(name)
                    else:
                        if date not in getattr(self, attr):
                            getattr(self, attr)[date] = {}
                        getattr(self, attr)[date][name] = answer

    def calc_motm(self):
        "Calc the MOTM for the previous game"
        self.get_team_data(['vote'])

        date = self.fixtures.previous_date.strftime('%Y-%m-%d')
        self.motm[date] = {} # create motm dict
        for id, user in self.team.items():

            # check if user has voted
            if date not in user.vote:
                continue

            # get vote
            vote = user.vote[date]
            # add vote to motm
            self.motm[date][vote] = self.motm[date].get(vote, 0) + 1

        # update users motm winners 
        top_votes = max(self.motm[date].values())

        for name, votes in self.motm[date].items():
            id = self.user_names[name]
            if votes == top_votes:
                self.team[id].motm[date] = votes

        self.save_team() # save data

    # =========================================================================
    # --------------------- Team commands -------------------------------------
    # =========================================================================

    @commands.command(name='available', aliases=['avaliable', 'availiable', 'avail', 'a'])
    async def available(self, ctx, *args):
        "mark availability for a given game"
        try:
            resp = args[0].lower()
        except IndexError:
            resp = 'yes'

        player, date = await self.args_player_date(ctx, args, 1, 2, prev_date=False)
        
        # check arguments
        if resp not in ['yes', 'y', 'no', 'n', 'maybe']:
            await ctx.send(f"Response must be 'yes', 'no' or 'maybe' - you entered {resp}")
            return
        if (player == False) or (date == False):
            return
        resp = 'yes' if resp in ['yes', 'y'] else 'no' if resp in ['no', 'n'] else 'maybe'
        
        # excute command
        display_name, id = player
        user = self.team[str(id)]

        await ctx.send(f'Set {user.display_name} availability to: {resp} for game on {date}')
        user.availability[date] = resp # update figures

        # add default paid response
        if resp == 'yes':
            user.paid[date] = user.paid.get(date, False)


        # notify Captain
        msg_user = self.team[str(ctx.author.id)].display_name
        if ctx.author.id != self.captain_id:
            await self.captain.send(f'Availability update: {msg_user} has marked **{user.display_name}** as **{resp}** for game on {date}')
        
        self.save_team() # save data

    @commands.command(name='paid', aliases=['p', 'piad', 'pay'])
    async def paid(self, ctx, *args):
        "Check who has paid for a given game"
        try:
            resp = args[0].lower()
        except IndexError:
            resp = 'yes'
            
        player, date = await self.args_player_date(ctx, args, 1, 2)

        # check arguments
        if resp not in ['yes', 'y', 'no', 'n']:
            await ctx.send(f"Response must be '!paid yes' or '!paid no' - you entered {resp}")
            return
        if (player == False) or (date == False):
            return
        
        resp = 'yes' if resp in ['yes', 'y'] else 'no'

        # excute command
        display_name, id = player
        user = self.team[str(id)]

        await ctx.send(f'Set {user.display_name} paid status to: {resp} for game on {date}')

        resp = True if resp == 'yes' else False
        user.paid[date] = resp # update figures


        # notify Captain
        msg_user = self.team[str(ctx.author.id)].display_name
        if ctx.author.id != self.captain_id:
            await self.captain.send(f'Paid update: {msg_user} has marked **{user.display_name}** as **{resp}** for game on {date}')

        self.save_team() # save data

    @commands.command(name='paid_all', aliases=['pa', 'piad_all', 'pay_all'])
    async def paid_all(self, ctx, *args):
        "Mark all payments as paid for a player"
        try:
            player = args[0]
        except IndexError:
            player = self.team[str(ctx.author.id)].display_name

        for id, user in self.team.items():
            # player not in team
            if player.lower() in user.name:
                player = [user.display_name, id] # found player
                break
        else:
            # Error - player not found
            await ctx.send(f'Player name: {player} not found - please try again')
            return
    
        # excute command
        outstanding = self.outstanding_dict()

        if player[0] not in outstanding:
            await ctx.send(f'{player[0]} has no outstanding payments')
            return
        
        payment_dates = []
        for date in outstanding[player[0]]:
            
            user = self.team[player[1]]
            user.paid[date] = True

            payment_dates.append(date)

        await ctx.send(f'All payments marked as paid for {player[0]}, for games on: {", ".join(payment_dates)}')


        # notify Captain
        msg_user = self.team[str(ctx.author.id)].display_name
        if ctx.author.id != self.captain_id:
            await self.captain.send(f'Paid update: {msg_user} has marked all payments as paid for **{player[0]}** for games on: {", ".join(payment_dates)}')


        self.save_team() # save data


    @commands.command()
    async def outstanding(self, ctx):
        "Check who has outstanding payments"
        
        outstanding = self.outstanding_dict()

        # create message
        if len(outstanding) == 0:
            await ctx.send('No outstanding payments')
            return

        msg = 'The following people have outstanding payments:\n'
        for name, dates in outstanding.items():
            msg += f'**{name}** - {len(dates)} games - {(", ".join(dates))}\n'
            
        await ctx.send(msg)
        return

    @commands.command()
    async def goal(self, ctx, *args):
        "Add a goal to a player"

        player, date = await self.args_player_date(ctx, args, 1, 2)
        # check arguments
        num_goals = args[0]
        num_goals = self.check_int(num_goals)

        if type(num_goals) != int:
            await ctx.send(f'Goals must be an integer - you entered {num_goals}')
            return
        if (player == False) or (date == False):
            return
        
        # excute command
        display_name, id = player

        user = self.team[str(id)]
        prev_fig = user.goal.get(date, 0)

        await ctx.send(f'Set {num_goals} goals to player {user.display_name}  (Date: {date}), previous result: {prev_fig}')
        user.goal[date] = num_goals # update figures
        
        self.save_team() # save data

    @commands.command()
    async def assist(self, ctx, *args):
        "Add an assist to a player"

        player, date = await self.args_player_date(ctx, args, 1, 2)
        # check arguments
        num_assists = args[0]

        num_assists = self.check_int(num_assists)
        if type(num_assists) != int:
            await ctx.send(f'Assists must be an integer - you entered {num_assists}')
            return
        if (player == False) or (date == False):
            return
        
        # excute command
        display_name, id = player

        user = self.team[str(id)]
        prev_fig = user.assist.get(date, 0)

        await ctx.send(f'Set {num_assists} assists to player {user.display_name}  (Date: {date}), previous result: {prev_fig}')
        user.assist[date] = num_assists # update figures

        self.save_team() # save data


    @commands.command(name='vote', aliases=['v','motm'])
    async def vote(self, ctx, *args):
        "Vote for motm"
        player, date = await self.args_player_date(ctx, args, 0, 1)
        if (player == False) or (date == False):
            return
        
        display_name, id = player
        if int(id) == ctx.author.id:
            await ctx.send('You cannot vote for yourself')
            return
        
        user = self.team[str(ctx.author.id)]
        # excute command
        v_user = self.team[str(id)]

        # check if user has already voted
        result = user.vote.get(date, False)
        if result:
            if result == v_user.display_name:
                await ctx.send(f'You have already voted for {result}')
                return
            else:
                await ctx.send(f'You have previously voted for {result}... I will change that')
        
        user.vote[date] = v_user.display_name # update figures

        await ctx.send(f'You have voted for {display_name} for motm on {date}')
        self.save_team() # save data

        
    @commands.command(name='next', aliases=['n'])
    async def next(self, ctx):
        "Show the next game date and time and the recent form of the opponent"

        msg = self.next_msg()

        dis_msg = await ctx.channel.send(msg)

        await dis_msg.add_reaction("⚽") # Yes
        await dis_msg.add_reaction("❌") # No
        await dis_msg.add_reaction("❔") # Maybe


    @commands.command()
    async def stats(self, ctx):
        """
        Creating a table of stats for a given data type
        columns = player | won | lost | draw | goals | assists | motm 
                    avg gf | avg ga | avg gd | avg pts
        """
        our_matches = self.fixtures.all_our_games
        table = player_stats(self.team, our_matches)

        await ctx.send(f'```{table.to_string(index=False)}```')

# =========================================================================
    # Emoji detection
    # =========================================================================

     # detect reactions on a message
    # function should detect: or oiginal msg, authorid, emoji, and emoji's user id
    def init_bot_event(self):

        @self.bot.event
        async def on_raw_reaction_add(payload):
            """Emoji Reactions - Detect reactions on a message"""
            # ---------------------------------------------------
            # get data emoji

            author_id = payload.message_author_id
            user_id = payload.user_id
            
            if (user_id == self.bot_id) or (author_id != self.bot_id):
            # ignore bot's reaction or not bot's message
                return

            # get message content
            msg_id = payload.message_id
            # Attempt to get the channel as a guild channel
            channel = self.bot.get_channel(int(payload.channel_id))
            if channel is None:  # If the channel doesn't exist, it might/should be a DM
                user = await self.bot.fetch_user(payload.user_id)  # Fetch the user by their ID
                channel = user.dm_channel  # Get the DM channel of the user

                if channel is None:  # If the DM channel doesn't exist, create it
                    # shouldn't fire
                    channel = await user.create_dm()

            message = await channel.fetch_message(msg_id)

            msg_content = message.content
            msg_dt = message.created_at
            msg_author_id = message.author
            user_emoji = payload.emoji.name

            user = self.team.get(str(user_id), False)
            if user == False:
                return
            # ---------------------------------------------------

            # availabilty message
            if msg_content.startswith("__**Next match**__"):

                # if msg date < last fixture date, ignore
                if self.fixtures.previous_date.replace(tzinfo=None) > msg_dt.replace(tzinfo=None):
                    
                    # send msg to user to say it was ignored
                    dis_user = self.bot.get_user(int(user_id))

                    msg = f'Your reaction to the next match message was ignored as the message was sent before the last game'
                    msg += f'\n\nPlease !n to get the next match message'

                    await dis_user.send(msg)

                    return
                
                if user_emoji in ['⚽', '❌', '❔']:
                    # get date
                    date = self.fixtures.upcoming_date.strftime('%Y-%m-%d')
                    response = 'yes' if user_emoji == '⚽' else 'no' if user_emoji == '❌' else 'maybe'
                    
                    user.availability[date] = response
                    # add default paid response
                    if response == 'yes':
                        user.paid[date] = user.paid.get(date, False)

                    self.save_team()
                    
                    await message.edit(content = self.next_msg())

                emoji_fn = "Next match"
            
            # paid message 
            if msg_content.startswith("__**Outstanding payments**__"):
                
                if user_emoji in ['💸','💰']:
                    
                    # 💸 paid this week
                    if user_emoji == '💸':
                        date = self.fixtures.previous_date.strftime('%Y-%m-%d')
                        user.paid[date] = True

                    # 💰 paid all
                    if user_emoji == '💰':
                        for date in self.outstanding_dict()[user.display_name]:
                            user.paid[date] = True
                
                    self.save_team()
                emoji_fn = "Outstanding payments"

            # vote message 
            if msg_content.startswith("__**Man of the Match**__"):
                emoji_fn = "MOTM"

                for id, player in self.team.items():

                    if user_emoji == player.emoji:
                        await self.captain.send(f'{user.display_name} has voted for {player.display_name}')

                        # cant vote for themselves
                        if int(id) == user_id:
                            dis_user = self.bot.get_user(int(user_id))
                            await dis_user.send('You cannot vote for yourself')
                            return
                        
                        # update vote
                        date = self.fixtures.previous_date.strftime('%Y-%m-%d')
                        user.vote[date] = player.display_name
                        self.save_team()
                        break

            # Message Captain
            await self.captain.send(f'{user.display_name} has reacted to the {emoji_fn} message with {user_emoji}')

    # =========================================================================
    # --------------------- Helper functions ----------------------------------
    # =========================================================================
    async def args_player_date(self, ctx, args, 
                         exp_player_ind: int, exp_date_ind: int,
                        prev_date: bool = True):
        """
        Helper function - try to determiner relevant parameters for  player and date
        
        Parameters
        ----------
        args: list of arguments
        exp_player_ind: expected index of player
        exp_date_ind: expected index of date
        prev_date: bool - if date is assumed previous date is given, otherwise it is next date
        """

        if str(ctx.author.id) not in self.team.keys(): # check user is part of team
            await ctx.send(f'You are not part of the team - please contact an admin')
            return False, False
        
        self.fixtures.get_fixture_info() 
        
        def check_player_date(player):
            "Helper - Check if player is a date"
            try:
                dateformat = ('%d/%m/%Y' if '/' in player else '%Y-%m-%d')
                dt.strptime(player, dateformat)
                return True
            except ValueError:
                return False

        # Determine discord user / player        
        # ---------------------------------------------------------------------
        try:
            player = args[exp_player_ind] # suspected player
            
            if not check_player_date(player): # check if player is a date input

                for id, user in self.team.items():
                    # player not in team
                    if player.lower() in user.name:
                        player = [user.display_name, id] # found player
                        break
                else:
                    # Error - player not found
                    await ctx.send(f'Player name: {player} not found - please try again')
                    return False, False
            else:
                # player is a date
                exp_date_ind = exp_player_ind
                display_name = self.users[str(ctx.author.id)]
                player = [display_name, ctx.author.id] # assume user is calling command
            
        except IndexError:
            # no player given - assume user is calling 
            display_name = self.users[str(ctx.author.id)]
            player = [display_name, ctx.author.id] 

        # Determine date
        # ---------------------------------------------------------------------
        try:
            date = args[exp_date_ind]
            
            dateformat = ('%d/%m/%Y' if '/' in date else '%Y-%m-%d')
            date = dt.strptime(date, dateformat)  

            if date.weekday() != 3:
                feedback = f'Date must be a Thursday - entered date ({date.date()}) is a ' \
                            + date.strftime('%A')
                
                # find closest dates
                match_data = self.fixtures.match_data
                next_date = match_data.loc[match_data['Date'] > date].iloc[0]['Date']
                prev_date = match_data.loc[match_data['Date'] < date].iloc[-1]['Date']

                feedback += f'\nClosest fixture dates are {prev_date.date()} and {next_date.date()}'

                await ctx.send(feedback)

                return False, False
        
        # Error handling
         
        except IndexError:
            # not enough arguments - assume date is latest 
            date = self.fixtures.previous_date if prev_date \
                            else self.fixtures.upcoming_date
            # removed for clutter
            # await ctx.send(f'No date given - assuming date: {date.date()}')
        
        except TypeError:
            # unrecognised date format
            feedback = 'Date must be in the format YYYY-MM-DD'
            await ctx.send(feedback)
            return False, False
        
        return player, date.strftime('%Y-%m-%d')
    
    def check_int(self, num):
        "Check if number is an integer"
        try:
            return int(num)
        except ValueError:
            return False
        
    def next_msg(self):
        "Generate the next game message"
        self.get_team_data(['availability'], group_answers = True)

        next_info, opponent_form, prev_match_opp, date = self.fixtures.next_game_info()

        # avaliablity of players
        avaliable_msg = '__**Team avaliability**__:\n\n'
        cur_team = self.availability.get(date, {})

        # player responses
            # yes - avaliable
        available_players = cur_team.get('yes',[])
        avaliable_msg += f"**Availaible** ({len(available_players)}): {', '.join(available_players)}\n"
            # no - not avaliable
        notavailable_players = cur_team.get('no',[])
        avaliable_msg += f"**Not Availaible** ({len(notavailable_players)}): {', '.join(notavailable_players)}\n"
            # maybe
        if 'maybe' in cur_team.keys():
            maybe_players = cur_team.get('maybe',[])
            avaliable_msg += f"\nMaybe ({len(maybe_players)}): {', '.join(maybe_players)}\n"
            # no response
        no_response = []
        for user in self.team.values():
            if not any(user.display_name in lst for lst in cur_team.values()):
                no_response.append(user.display_name)

        if len(no_response) > 0:
            avaliable_msg += f'\nNo response ({len(no_response)}): {", ".join(no_response)}'
 
        msg ='__**Next match**__\n' # Emoji identifier
        msg += next_info + '\n' + prev_match_opp + '\n\n'
        msg += avaliable_msg + '\n\n' + opponent_form 
        msg += '\n\nTo update your availability please react to this message!'
        return msg
        
    def outstanding_dict(self):
        "Get the outstanding payments as a dictionary"
        
        outstanding = {} # Name: [dates]
        self.get_team_data(['paid'], group_answers = True)

        for date, val in self.paid.items():

            if False in val:
                for name in val[False]:
                    if name not in outstanding:
                        outstanding[name] = []
                    outstanding[name].append(date)

        return outstanding

        
    # =========================================================================
    # Import and exporting team data to json
    # =========================================================================

    def load_team(self):
        "Import team data from json to Player classes"
    
        with open(self.path + 'user_data/team_data.json', 'r') as f:
            self.user_data = json.load(f)

        self.team = {} # team data

        for id, val in self.user_data.items():

            user = Player(name = val['Name'], 
                        id = id,
                        availability = val['avaliability'],
                        paid = val['paid'],
                        goal = val['goal'],
                        assist = val['assist'],
                        vote = val['vote'],
                        motm = val['motm'],
                        )
            # add user to team
            self.team[id] = user

        # id to user mapping
        self.users = {id: user.display_name for id, user in self.team.items()}
        self.user_names = {user.display_name: id for id, user in self.team.items()}


    def save_team(self):
        "Export team data from all Player classes to a json"
        data_out = {}
        for id, val in self.team.items():
            data_out[id] = {}

            data_out[id]['Name'] = val.name
            data_out[id]['avaliability'] = val.availability
            data_out[id]['paid'] = val.paid
            data_out[id]['goal'] = val.goal
            data_out[id]['assist'] = val.assist
            data_out[id]['vote'] = val.vote
            data_out[id]['motm'] = val.motm

        with open(self.path + 'user_data/team_data.json', 'w') as f:
            json.dump(data_out, f, indent=4)

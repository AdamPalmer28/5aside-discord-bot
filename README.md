# Disord bot for local discord server

Bot handles tracking for 5 aside team.
Bot is a rest API to a server hosting team data.

### Commands:

General:

- !commands - shows help

Availability:

- !available <yes/no/maybe> <player> <game date>
- !paid <yes/no> <player> <game date>
- !outstanding - shows who has not paid

Results:

- !recent - shows recent results
- !table - shows league table
- !next - shows next game details
- !stats - shows player stats

Player stats

- !goal <num of goals> <player> <game date> - set number of goals for player at game date
- !assist <num of goals> <player> <game date> - set number of assists for player at game date
- !vote <player> <game date> - Vote for a motm player

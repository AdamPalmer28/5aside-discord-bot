# Discord bot for local discord server

_Bot handles management of our local 5 aside team as well as updating the team on fixutres and results_

Bot acts as middle group to a rest API to a server hosting team data, fixtures, and results.

**Core Features:**

- Results and fixture tracking (extracted via webscraping)
- Player/team availability and payment tracking
- Player stats: Goals, Assists, and MOTM
- User chasing/follow-up on avaliabilty, payment & MoTM voting

---

### Commands:

User commands called via discord chat

General:

- !commands - shows commands avaliable to users

Availability:

- !available <yes/no/maybe> <player> <game_date>
- !paid <yes/no> <player> <game_date>
- !outstanding - shows who has not paid

Results:

- !recent - shows recent results
- !table - shows league table
- !next - shows next game details
- !stats - shows player stats

Player stats

- !goal <num of goals> <player> <game_date> - set number of goals for player at game date
- !assist <num of goals> <player> <game_date> - set number of assists for player at game date
- !vote <player> <game_date> - Vote for a motm player

Parameters **player** and **game_date** are both optional inputs (in most cases), where they are not provided this the player is assumed to be the user (i.e. the message sender) and the date is assumed to be the most relevant date (usually previous match date - except !avaliable where assumed date is upcoming match).

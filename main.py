import discord
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from discord.ext import commands
from discord.utils import get
import logging
import teams
from itertools import accumulate

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

with open("config.json") as f:
    config = json.load(f)
    token = config["TOKEN"]
    project_id = config["PROJECT_ID"]

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': project_id,
})

db = firestore.client()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

sudo = commands.Bot(intents=intents, command_prefix='!')

@sudo.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(sudo))

#Takes in user points based on specific reactions
# TODO: Add score for multiple reactions (I.e. this currently stops after one reaction)
# Afterwards add a feature that only allows users to get max one point per message 
# Create team database which is better for data management
# Team Database 
#   Team A: Obj -> {Name (Str), Emote (Str), Points (Int), Members (List)}
#   Team B: Obj -> {Name (Str), Emote (Str), Points (Int), Members (List)}
#   Team C: Obj -> {Name (Str), Emote (Str), Points (Int), Members (List)}
# Divide the code into multiple files

#Completely resets the team statistics table by creating entirely new teams
@sudo.command()
@commands.has_permissions(administrator=True)
async def addTeams(ctx, team_count):
    team_num = 0
    for team_num in range(int(team_count)):
        team_letter = str(chr(ord('@') + (team_num + 1)))
        team_ref = db.collection('teams').document(team_letter)
        team_ref.set ({
            'team_name': "team_" + team_letter,
            'emote': team_letter,
            'points': 0,
            'member_list': [],
            'member_count': 0,
        })
        team_name = team_ref.get().get("team_name")
        await ctx.send(f"{team_name} has been created")

# #TODO: Make a function that deletes all teams from database
@sudo.command()
@commands.has_permissions(administrator=True)
async def removeAllTeams(ctx):
    team_ref = db.collection(u'teams')
    docs = team_ref.stream()
    for doc in docs:
        await ctx.send(f'{doc.id} is being removed')
        db.collection(u'teams').document(str(doc.id)).delete()
        
@sudo.command()
async def viewTeams(ctx):
    team_ref = db.collection(u'teams')
    docs = team_ref.stream()
    for doc in docs:
        await ctx.send(f'{doc.id} => {doc.to_dict()}')

#Gets the number of people that are currently on a specific team
@sudo.command()
async def getTeamCount(ctx, team_name):
    count = 0
    user_ref = db.collection(u'users')
    docs = user_ref.stream()
    for doc in docs:
        doc_ref = db.collection('users').document(str(doc.id))
        if (doc_ref.get().get("team") == team_name):
            count += 1
    await ctx.send(f"teamcount is {count}")
    return count

#Gets the number of people that are participating in the habits competition
@sudo.command()
async def getMemberCount(ctx):
    count = 0
    user_ref = db.collection(u'users')
    docs = user_ref.stream()
    for x in docs:
        count += 1
    await ctx.send(f"member count is {count}")
    return count

@sudo.command()
@commands.has_permissions(administrator=True)
async def assignTeams(ctx, number_of_teams):
    #TODO: Assign each member to a random team
    #Make sure that each team has an equal number of people
    #number of people playing
    member_count = await getMemberCount(ctx)
    user_ref = db.collection(u'users')
    docs = user_ref.stream()
    if number_of_teams % member_count != 0:
        await ctx.send("teams are unequal, please try again")
        return
    team_member_count = member_count / number_of_teams
    
    
    return

@sudo.command()
async def react(ctx):
    user_ref = db.collection('users').document(str(ctx.author.id))
    teams = {
        "team_A": "🇦",
        "team_B": "🇧",
        "team_C": "🇨"
    }
    await ctx.send("This is the daily message!")  # Message to react to
    reaction = await sudo.wait_for("reaction_add")  # Wait for a reaction
    userTeam = user_ref.get().get("team")
    if str(reaction[0]) == teams[(userTeam)]:
        await addLogs(ctx, 1)

@sudo.command()
async def viewUserData(ctx):
    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        await ctx.send(f'{doc.id} => {doc.to_dict()}')

#adds user token amount
@sudo.command()
@commands.has_permissions(administrator=True)
async def addToken(ctx, token_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    tokens = doc_ref.get().get("tokens") + int(token_count)
    doc_ref.update({"tokens": firestore.Increment(int(token_count))})
    await ctx.send(f"Added {int(token_count)} tokens. {ctx.author} now has {tokens} tokens")

#adds monthly logs
@sudo.command()
@commands.has_permissions(administrator=True)
async def addLogs(ctx, monthly_log_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    monthly_logs = doc_ref.get().get("monthly_logs") + int(monthly_log_count)
    doc_ref.update({"monthly_logs": firestore.Increment(int(monthly_log_count))})
    await ctx.send(f"Added {int(monthly_log_count)} monthly logs. {ctx.author} now has {monthly_logs} logs completed")

#change team 
@sudo.command()
@commands.has_permissions(administrator=True)
async def changeTeam(ctx, *, team_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"team": team_name})
    await ctx.send(f"{ctx.author} team is now {team_name}")

#change habit
@sudo.command()
@commands.has_permissions(administrator=True)
async def changeHabit(ctx, *, habit_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"habit": habit_name})
    await ctx.send(f"{ctx.author}'s habit is now {habit_name}")

#sets user stats for tokens, quests, monthly logs, team, and habit
@sudo.command()
@commands.has_permissions(administrator=True)
async def setUserStats(ctx, token_count, monthly_log_count, team_name, habit_name, quest_count, streak_count, mvp_count, win_count, purchase_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'tokens': int(token_count),
        'monthly_logs': int(monthly_log_count),
        'team': team_name,
        'habit': habit_name,
        'quests': int(quest_count),
        'streaks': int(streak_count),
        'mvp': int(mvp_count),
        'wins': int(win_count),
        'purchases': int(purchase_count)

    })
    await ctx.send(f"User stats for {ctx.author} has been set")

#allows user to view their own personal stats
@sudo.command()
async def viewStats(ctx, arg=None):
    user = ctx.author
    doc_ref = db.collection('users').document(str(user.id))
    tokens = doc_ref.get().get("tokens")
    monthly_logs = doc_ref.get().get("monthly_logs")
    team = doc_ref.get().get("team")
    habit = doc_ref.get().get("habit")
    await ctx.send(f"**Personal Stats for {ctx.author}** \n ```Tokens: {tokens} \nMonthly Logs: {monthly_logs} \nTeam: {team} \nHabit: {habit}``` ")

#allows user to take a deeper look into how their tokens are calculated
@sudo.command()
async def viewCalculations(ctx, arg=None):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    tokens = doc_ref.get().get("tokens")
    quests = doc_ref.get().get("quests")
    streaks = doc_ref.get().get("streaks")
    mvp = doc_ref.get().get("mvp")
    wins = doc_ref.get().get("wins")
    purchases = doc_ref.get().get("purchases")
    await ctx.send(f"**Token Calculations for {ctx.author}** \n ```Tokens: {tokens} \nQuests {quests} \nStreaks: {streaks} \nMVP: {mvp} \nWins:  {wins} \nPurchases: {purchases}``` ")


#add commands for tokens database

#adds the total quest count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addQuests(ctx, quest_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(quest_count) * 10)})
    doc_ref.update({"quests": firestore.Increment(int(quest_count))})
    tokens = doc_ref.get().get("tokens")
    quests = doc_ref.get().get("quests")
    await ctx.send(f"Added {int(quest_count)} quests and now {ctx.author} has {quests} quests completed in total. {ctx.author} has also gained {int(quest_count) * 10} tokens and now has a total of {tokens} tokens.")

#adds the total streak count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addStreaks(ctx, streak_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(streak_count) * 30)})
    doc_ref.update({"quests": firestore.Increment(int(streak_count))})
    tokens = doc_ref.get().get("tokens")
    streaks = doc_ref.get().get("streaks")
    await ctx.send(f"Added {int(streak_count)} streaks and now {ctx.author} has {streaks} streaks completed in total. {ctx.author} has also gained {int(streak_count) * 30} tokens and now has a total of {tokens} tokens.")

#adds the total MVP count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addMVP(ctx, mvp_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(mvp_count) * 100)})
    doc_ref.update({"mvp": firestore.Increment(int(mvp_count))})
    tokens = doc_ref.get().get("tokens")
    mvp = doc_ref.get().get("mvp")
    await ctx.send(f"Added {int(mvp_count)} MVPs and now {ctx.author} has {mvp} MVPs earned in total. {ctx.author} has also gained {int(mvp) * 100} tokens and now has a total of {tokens} tokens.")

#adds the total win count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addWins(ctx, win_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(win_count) * 700)})
    doc_ref.update({"wins": firestore.Increment(int(win_count))})
    tokens = doc_ref.get().get("tokens")
    wins = doc_ref.get().get("wins")
    await ctx.send(f"Added {int(win_count)} wins and now {ctx.author} has {wins} wins earned in total. {ctx.author} has also gained {int(win_count) * 700} tokens and now has a total of {tokens} tokens.")

#adds to pruchase amount
@sudo.command()
@commands.has_permissions(administrator=True)
async def addPurchases(ctx, purchase_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(purchase_count) * -1)})
    doc_ref.update({"purchases": firestore.Increment(int(purchase_count))})
    tokens = doc_ref.get().get("tokens")
    purchases = doc_ref.get().get("purchases")
    await ctx.send(f"Spent {int(purchase_count)} tokens on purchases with a total spending of {purchases}. {ctx.author} now has {tokens} remaining.")


@sudo.command()
async def checkUsername(ctx):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    username = doc_ref.get().get("username")
    await ctx.send(f"Username is {username}")

@sudo.command()
async def listUsers(ctx):
    users = ctx.guild.members
    await ctx.send(f"{[str(i) for i in users]}")

def userSearch(guild, userkey):
    """user_search searches for a user in a guild by username#discriminator, username, or user_id"""
    users = guild.members
    results = []
    for i in users:
        if i.name == userkey:
            results.append(i)
            continue
        if i.id == userkey:
            results.append(i)
            continue
        if str(i) == userkey:
            results.append(i)
            continue
    return results

#mass updates user tokens by taking in an import list 
#TODO: Team and habit columns can only take in one word, potential solution is converting this function to import a CSV
@sudo.command()
@commands.has_permissions(administrator=True)
async def importUserData(ctx):
    message = ctx.message.content
    errors = []
    message_list = message.split("\n")[1:]
    users = {}
    for i, row in enumerate(message_list):
        columns = row.rsplit(maxsplit=9)
        if len(columns) != 10:
            errors.append(f"could not parse row {i+1}, must have a value for username, token, monthly logs, team name, and habit name")
        username = columns[0]
        try:
            userinfo = {
                "username": str(username),
                "tokens": int(columns[1]),
                "monthly_logs": int(columns[2]),
                "team":  str(columns[3]),
                "habit": str(columns[4]),
                'quests': int(columns[5]),
                'streaks': int(columns[6]),
                'mvp': int(columns[7]),
                'wins': int(columns[8]),
                'purchases': int(columns[9])
                }
        except ValueError:
            errors.append(f"ValueError {username} is ambiguous on row {i+1}")
        usermatch = userSearch(ctx.guild, username)
        if len(usermatch) > 1:
            errors.append(f"{username} is ambiguous on row {i+1}")
            continue
        elif len(usermatch) == 0:
            errors.append(f"{username} not found on row {i+1}")
            continue
        else:
            user = usermatch[0]
            users[str(user.id)] = userinfo
    if len(errors) > 0:
        await ctx.send(f"Error(s) parsing import command: {errors}")
    batch = db.batch()
    for i, v in users.items():
        doc_ref = db.collection('users').document(i)
        batch.set(doc_ref, v, merge=True)
    batch.commit()
    await ctx.send("Updated user values")

# Creates a list of all the users with their token details
@sudo.command()
@commands.has_permissions(administrator=True)
async def listAllTokenDetails(ctx):
    members = ctx.guild.members
    user_table = [("Name", "Tokens", "Quests", "Streaks", "MVPs", "Wins")]
    for i in members:
        if i.bot:
            continue
        doc_ref = db.collection('users').document(str(i.id))
        user = doc_ref.get()
        if user.exists:
            token = user.get('tokens')
            quests = user.get("quests")
            streaks = user.get('streaks')
            mvp = user.get("mvp")
            wins = user.get("wins")
        else:
            token = 0
        user_table.append((str(i), token, quests, streaks, mvp, wins))
    user_table[1:] = sorted(user_table[1:], key=lambda x: x[1], reverse=True)
    message = [f"{name:<30}{tokens:<10}{quests:<10}{streaks:<10}{mvp:<10}{wins:<10}" for name, tokens, quests, streaks, mvp, wins in user_table]
    await ctx.send("```" + "\n".join(message) + "```")

# Creates a list of all the users with their token details
@sudo.command()
@commands.has_permissions(administrator=True)
async def listAllTeamDetails(ctx):
    members = ctx.guild.members
    user_table = [("Name", "Team", "Habit")]
    for i in members:
        if i.bot:
            continue
        doc_ref = db.collection('users').document(str(i.id))
        user = doc_ref.get()
        if user.exists:
            team = user.get('team')
            habit = user.get('habit')
        else:
            token = 0
        user_table.append((str(i), team, habit))
    user_table[1:] = sorted(user_table[1:], key=lambda x: x[1], reverse=True)
    message = [f"{name:<30}{team:<20}{habit:<30}" for name, team, habit in user_table]
    await ctx.send("```" + "\n".join(message) + "```")

sudo.run(token, log_handler=handler)

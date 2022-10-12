import discord
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from discord.ext import commands
from discord.utils import get
import logging

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
    print("checking print statement!")
    print(discord.__version__)
    print("Logged in as a bot {0.user}".format(sudo))

#Takes in user points based on specific reactions
@sudo.command()
async def react(ctx):
    count = 0
    def check(reaction, user):  # Our check for the reaction        
        return user == ctx.message.author  # We check that only the authors reaction counts

    await ctx.send("Please react to the message!")  # Message to react to

    reaction = await sudo.wait_for("reaction_add", check=check)  # Wait for a reaction
    count += 1
    await ctx.send(f"count increased by 1, it is currently {count} ")
    await ctx.send(f"You reacted with: {reaction[0]}")  # With [0] we only display the emoji

@sudo.command()
async def viewUserData(ctx):
    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        await ctx.send(f'{doc.id} => {doc.to_dict()}')

@sudo.command()
async def viewTokenData(ctx):
    tokens_ref = db.collection(u'rewards')
    docs = tokens_ref.stream()
    if tokens_ref:
        await ctx.send(docs)
        await ctx.send("database not accessed")
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
async def setUserStats(ctx, token_count, monthly_log_count, team_name, habit_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'tokens': int(token_count),
        'monthly_logs': int(monthly_log_count),
        'team': team_name,
        'habit': habit_name,
    })
    await ctx.send(f"User stats for {ctx.author} has been set")

#allows user to view their own personal stats
@sudo.command()
async def viewUserStats(ctx, arg=None):
    user = ctx.author
    doc_ref = db.collection('users').document(str(user.id))
    tokens = doc_ref.get().get("tokens")
    monthly_logs = doc_ref.get().get("monthly_logs")
    team = doc_ref.get().get("team")
    habit = doc_ref.get().get("habit")
    await ctx.send(f"**Personal Stats for {ctx.author}** \n ```Tokens: {tokens} \nMonthly Logs: {monthly_logs} \nTeam: {team} \nHabit: {habit}``` ")

#add commands for tokens database

#adds the total quest count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addQuests(ctx, quest_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(quest_count) * 10)})
    doc_ref.update({"quests": firestore.Increment(int(quest_count))})
    tokens = doc_ref.get().get("tokens")
    quests = doc_ref.get().get("quests")
    await ctx.send(f"Added {int(quest_count)} quests and now {ctx.author} has {quests} quests completed in total. {ctx.author} has also gained {int(quest_count) * 10} tokens and now has a total of {tokens} tokens.")

#adds the total streak count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addStreaks(ctx, streak_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(streak_count) * 30)})
    doc_ref.update({"quests": firestore.Increment(int(streak_count))})
    tokens = doc_ref.get().get("tokens")
    streaks = doc_ref.get().get("streaks")
    await ctx.send(f"Added {int(streak_count)} streaks and now {ctx.author} has {streaks} streaks completed in total. {ctx.author} has also gained {int(streak_count) * 30} tokens and now has a total of {tokens} tokens.")

#adds the total MVP count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addMVP(ctx, mvp_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(mvp_count) * 100)})
    doc_ref.update({"mvp": firestore.Increment(int(mvp_count))})
    tokens = doc_ref.get().get("tokens")
    mvp = doc_ref.get().get("mvp")
    await ctx.send(f"Added {int(mvp_count)} MVPs and now {ctx.author} has {mvp} MVPs earned in total. {ctx.author} has also gained {int(mvp) * 100} tokens and now has a total of {tokens} tokens.")

#adds the total win count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addWins(ctx, win_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(win_count) * 700)})
    doc_ref.update({"wins": firestore.Increment(int(win_count))})
    tokens = doc_ref.get().get("tokens")
    wins = doc_ref.get().get("wins")
    await ctx.send(f"Added {int(win_count)} wins and now {ctx.author} has {wins} wins earned in total. {ctx.author} has also gained {int(wins) * 700} tokens and now has a total of {tokens} tokens.")

#adds to pruchase amount
@sudo.command()
@commands.has_permissions(administrator=True)
async def addPurchases(ctx, purchase_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.update({"tokens": firestore.Increment(int(purchase_count) * -1)})
    doc_ref.update({"pruchases": firestore.Increment(int(purchase_count))})
    tokens = doc_ref.get().get("tokens")
    purchases = doc_ref.get().get("purchases")
    await ctx.send(f"Spent {int(purchase_count)} tokens on purchases with a total spending of {purchases}. {ctx.author} now has {tokens} remaining.")

#sets user database regarding all the token details
@sudo.command()
@commands.has_permissions(administrator=True)
async def setTokenDetails(ctx, token_count, quest_count, streak_count, mvp_count, win_count, purchase_count):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    doc_ref.set({
        'user': ctx.author,
        'tokens': int(token_count),
        'quests': int(quest_count),
        'streaks': int(streak_count),
        'mvp': int(mvp_count),
        'wins': int(win_count),
        'purchases': int(purchase_count)
    })
    await ctx.send(f"**{ctx.author}'s token details have been set**")

#allows user to view their own personal stats regarding token details
@sudo.command()
async def viewTokenDetails(ctx, arg=None):
    doc_ref = db.collection('rewards').document(str(ctx.author.id))
    user = doc_ref.get().get("user")
    tokens = doc_ref.get().get("tokens")
    quests = doc_ref.get().get("quests")
    streaks = doc_ref.get().get("streaks")
    mvp = doc_ref.get().get("mvp")
    wins = doc_ref.get().get("wins")
    purchases = doc_ref.get().get("purchases")
    await ctx.send(f"**Setting Stats for {user}** \n ```Tokens: {tokens} \nQuests {quests} \nStreaks: {streaks} \nMVP: {mvp} \nWins:  {wins} \nPurchases: {purchases}``` ")

@sudo.command()
async def checkUsername(ctx):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    username = doc_ref.get().get("username")
    print("ctx is: ", ctx)
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
@sudo.command()
@commands.has_permissions(administrator=True)
async def importTokens(ctx):
    message = ctx.message.content
    errors = []
    message_list = message.split("\n")[1:]
    users = {}
    for i, row in enumerate(message_list):
        columns = row.rsplit(maxsplit=1)
        if len(columns) != 2:
            errors.append(f"could not parse row {i+1}, must have 1 username and 1 token value per row")
        username = columns[0]
        try:
            tokens = int(columns[1])
        except ValueError:
            errors.append(f"{username} is ambiguous on row {i+1}")
        usermatch = userSearch(ctx.guild, username)
        if len(usermatch) > 1:
            errors.append(f"{username} is ambiguous on row {i+1}")
            continue
        elif len(usermatch) == 0:
            errors.append(f"{username} not found on row {i+1}")
            continue
        else:
            user = usermatch[0]
            users[str(user.id)] = tokens
    if len(errors) > 0:
        await ctx.send(f"Error(s) parsing import command: {errors}")
    batch = db.batch()
    for i, v in users.items():
        doc_ref = db.collection('users').document(i)
        batch.set(doc_ref, {"tokens": v}, merge=True)
    batch.commit()
    await ctx.send("Updated user tokens")

# Creates a list of all the users with their token value
@sudo.command()
@commands.has_permissions(administrator=True)
async def listTokens(ctx):
    members = ctx.guild.members
    tokens_table = [("Name", "Tokens")]
    for i in members:
        if i.bot:
            continue
        doc_ref = db.collection('users').document(str(i.id))
        user = doc_ref.get()
        if user.exists:
            token = user.get('tokens')
        else:
            token = 0
        tokens_table.append((str(i), token))
    tokens_table[1:] = sorted(tokens_table[1:], key=lambda x: x[1], reverse=True)
    message = [f"{name:<30}{tokens:<10}" for name, tokens in tokens_table]
    await ctx.send("```" + "\n".join(message) + "```")

sudo.run(token, log_handler=handler)

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
    tokens_ref = db.collection(u'tokens')
    docs = tokens_ref.stream()

    for doc in docs:
        await ctx.send(f'{doc.id} => {doc.to_dict()}')

#adds user token amount
@sudo.command()
@commands.has_permissions(administrator=True)
async def addToken(ctx, token_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    user = doc_ref.get()
    tokens = user.get("tokens") + int(token_count)
    doc_ref.set({
        'tokens': tokens,
        'quests': user.get("quests"),
        'monthly_logs': user.get("monthly_logs"),
        'team': user.get("team"),
        'habit': user.get("habit")
    })
    await ctx.send(f"Added {int(token_count)} tokens. {ctx.author} now has {tokens} tokens")

#adds the total quest count
@sudo.command()
@commands.has_permissions(administrator=True)
async def addQuests(ctx, quest_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    user = doc_ref.get()
    quests = user.get("quests") + int(quest_count)
    doc_ref.set({
        'tokens': user.get("tokens"),
        'quests': quests,
        'monthly_logs': user.get("monthly_logs"),
        'team': user.get("team"),
        'habit': user.get("habit")
    })
    await ctx.send(f"Added {int(quest_count)} completed quests. {ctx.author} now has {quests} quests completed")

#adds monthly logs
@sudo.command()
@commands.has_permissions(administrator=True)
async def addLogs(ctx, monthly_log_count):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    user = doc_ref.get()
    monthly_logs = user.get("monthly_logs") + int(monthly_log_count)
    doc_ref.set({
        'tokens': user.get("tokens"),
        'quests': user.get("quests"),
        'monthly_logs': monthly_logs,
        'team': user.get("team"),
        'habit': user.get("habit")
    })
    await ctx.send(f"Added {int(monthly_log_count)} monthly logs. {ctx.author} now has {monthly_logs} logs completed")

#change team 
@sudo.command()
@commands.has_permissions(administrator=True)
async def changeTeam(ctx, *, team_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    user = doc_ref.get()
    doc_ref.set({
        'tokens': user.get("tokens"),
        'quests': user.get("quests"),
        'monthly_logs': user.get("monthly_logs"),
        'team': team_name,
        'habit': user.get("habit")
    })
    await ctx.send(f"{ctx.author} team is now {team_name}")

#change habit
@sudo.command()
@commands.has_permissions(administrator=True)
async def changeHabit(ctx, *, habit_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    user = doc_ref.get()
    doc_ref.set({
        'tokens': user.get("tokens"),
        'quests': user.get("quests"),
        'monthly_logs': user.get("monthly_logs"),
        'team': user.get("team"),
        'habit': habit_name
    })
    await ctx.send(f"{ctx.author}'s habit is now {habit_name}")

#sets user stats for tokens, quests, monthly logs, team, and habit
@sudo.command()
@commands.has_permissions(administrator=True)
async def setUserStats(ctx, token_count, quest_count, monthly_log_count, team_name, habit_name):
    doc_ref = db.collection('users').document(str(ctx.author.id))
    doc_ref.set({
        'tokens': int(token_count),
        'quests': int(quest_count),
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
    quests = doc_ref.get().get("quests")
    monthly_logs = doc_ref.get().get("monthly_logs")
    team = doc_ref.get().get("team")
    habit = doc_ref.get().get("habit")
    await ctx.send(f"**Personal Stats for {ctx.author}** \n ```Tokens: {tokens} \nQuests {quests} \nMonthly Logs: {monthly_logs} \nTeam: {team} \nHabit: {habit}``` ")

#sets user database regarding all the token details
@sudo.command()
@commands.has_permissions(administrator=True)
async def setTokenDetails(ctx, token_count, quest_count, streak_count, mvp_count, win_count, purchase_count):
    doc_ref = db.collection('tokens').document(str(ctx.author.id))
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

#allows user to view their own personal stats
@sudo.command()
async def viewTokenDetails(ctx, arg=None):
    doc_ref = db.collection('tokens').document(str(ctx.author.id))
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
